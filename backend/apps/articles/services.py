"""
Business logic shared between the Django Admin actions (the actual
human-facing UI for the technical editor — see M3b plan decision #1) and the
REST endpoints documented in TS section 7 (decision #2): one implementation,
two entry points.
"""

import uuid

from django.db.models import Max
from django.utils import timezone

from apps.editorial.models import EditorialDecision
from apps.notifications.models import Notification
from apps.reviews.models import Review
from apps.users.models import Role, User

from .models import Article, ArticleVersion


def approve_completeness(article: Article, editor) -> Article:
    """US-2: materials are complete — hand off to the chief editor's queue (US-4, not built yet)."""
    article.completeness_approved_at = timezone.now()
    article.save(update_fields=["completeness_approved_at"])
    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=EditorialDecision.ACCEPT,
        stage=EditorialDecision.COMPLETENESS_CHECK,
        comment="",
    )
    return article


def return_for_revision(article: Article, editor, comment: str) -> Article:
    """US-2: incomplete materials — comment is mandatory (PRD section 7 business rule)."""
    if not comment or not comment.strip():
        raise ValueError("Комментарий обязателен при возврате статьи на доработку.")

    article.status = Article.NEEDS_REVISION
    article.save(update_fields=["status"])

    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=EditorialDecision.REVISE,
        stage=EditorialDecision.COMPLETENESS_CHECK,
        comment=comment,
    )
    Notification.objects.create(
        user=article.submitted_by,
        article=article,
        type=Notification.STATUS_CHANGED,
        message=f"Статья «{article.title_ru}» возвращена на доработку: {comment}",
    )
    return article


def approve_topic(article: Article, editor) -> Article:
    """
    US-4: article fits the journal's scope. No status change — PRD only
    assigns a new status once ALL assigned reviewers accept (US-5); until
    then "submitted" still covers this sub-stage (see M3c plan decision #1).
    """
    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=EditorialDecision.ACCEPT,
        stage=EditorialDecision.TOPIC_CHECK,
        comment="",
    )
    return article


def reject_topic(article: Article, editor, comment: str) -> Article:
    """US-4: article doesn't fit the journal's scope — comment is mandatory (PRD section 7)."""
    if not comment or not comment.strip():
        raise ValueError("Комментарий обязателен при отклонении статьи.")

    article.status = Article.REJECTED
    article.save(update_fields=["status"])

    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=EditorialDecision.REJECT,
        stage=EditorialDecision.TOPIC_CHECK,
        comment=comment,
    )
    Notification.objects.create(
        user=article.submitted_by,
        article=article,
        type=Notification.STATUS_CHANGED,
        message=f"Статья «{article.title_ru}» отклонена: {comment}",
    )
    return article


def make_review_decision(article: Article, editor, decision: str, comment: str) -> Article:
    """
    US-7: final decision once every accepted reviewer has submitted. Comment
    is mandatory for all three outcomes here (see DecisionInputSerializer).
    """
    if article.status != Article.IN_REVIEW:
        raise ValueError("Статья не находится на этапе рецензирования.")
    if article.reviews.filter(invitation_status=Review.ACCEPTED, submitted_at__isnull=True).exists():
        raise ValueError("Ещё не все рецензии получены.")

    status_by_decision = {
        EditorialDecision.ACCEPT: Article.ACCEPTED,
        EditorialDecision.REJECT: Article.REJECTED,
        EditorialDecision.REVISE: Article.NEEDS_REVISION,
    }
    article.status = status_by_decision[decision]
    article.save(update_fields=["status"])

    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=decision,
        stage=EditorialDecision.REVIEW_DECISION,
        comment=comment,
    )
    Notification.objects.create(
        user=article.submitted_by,
        article=article,
        type=Notification.DECISION_MADE,
        message=(
            f"Решение по статье «{article.title_ru}»: {comment}. "
            "Комментарии рецензентов доступны на странице статьи."
        ),
    )
    return article


def add_revision_version(
    article: Article,
    manuscript_file,
    documents_files,
    document_types,
    author_comment: str,
) -> ArticleVersion:
    """US-3/US-7 revise outcome: author uploads a corrected version after being sent back for revision."""
    next_number = (article.versions.aggregate(Max("version_number"))["version_number__max"] or 0) + 1
    version = ArticleVersion.objects.create(
        article=article,
        version_number=next_number,
        manuscript_file=manuscript_file,
        author_comment=author_comment or "",
    )
    for idx, file in enumerate(documents_files or []):
        doc_type = document_types[idx] if document_types and idx < len(document_types) else ""
        version.documents.create(doc_type=doc_type, file=file)

    # PRD section 7: a resubmitted revision returns to the stage it was sent
    # back from — branch on the most recent "revise" EditorialDecision.
    last_revise = article.decisions.filter(decision=EditorialDecision.REVISE).order_by("-created_at").first()

    if last_revise and last_revise.stage == EditorialDecision.REVIEW_DECISION:
        # US-8: sent back after peer review — old reviews no longer apply to
        # the new version. Deleting rather than flagging them "superseded"
        # (no such field on Review, and adding one now is more than closing
        # US-7's revise outcome calls for — see M3e plan #4). The chief
        # editor re-assigns reviewers, same or new, via the queue they
        # already have (M3c) once this makes `article.reviews` empty again.
        article.reviews.all().delete()
        article.status = Article.SUBMITTED
        article.save(update_fields=["status"])
        for chief_editor in User.objects.filter(roles__code=Role.CHIEF_EDITOR).distinct():
            Notification.objects.create(
                user=chief_editor,
                article=article,
                type=Notification.STATUS_CHANGED,
                message=f"Автор загрузил исправленную версию статьи «{article.title_ru}» — назначьте рецензентов заново.",
            )
    else:
        # Default / completeness-check path (M3b): back to the tech-editor queue.
        article.status = Article.SUBMITTED
        article.completeness_approved_at = None
        article.save(update_fields=["status", "completeness_approved_at"])

    return version


def assign_doi(article: Article, editor) -> Article:
    """
    US-9: placeholder DOI generation — PRD section 8 (risks) explicitly
    allows manual/stand-in DOIs as a stopgap until a real CrossRef/НЭИКОН
    integration exists. Uniqueness is checked here (retry-on-collision)
    rather than a DB unique index — see M3f plan decision #2.
    """
    if article.status != Article.ACCEPTED:
        raise ValueError("DOI можно присвоить только статье в статусе «Принята к публикации».")
    if article.doi:
        raise ValueError("Статье уже присвоен DOI.")

    year = timezone.now().year
    for _ in range(5):
        candidate = f"10.36622/vstu.{year}.{uuid.uuid4().hex[:8]}"
        if not Article.objects.filter(doi=candidate).exists():
            article.doi = candidate
            break
    else:
        raise ValueError("Не удалось сгенерировать уникальный DOI, попробуйте ещё раз.")

    article.save(update_fields=["doi"])
    return article


def publish_article(article: Article, editor, issue) -> Article:
    """US-9: PRD section 7 — no publication without a DOI and without an issue."""
    if article.status != Article.ACCEPTED:
        raise ValueError("Опубликовать можно только статью в статусе «Принята к публикации».")
    if not article.doi:
        raise ValueError("Присвойте DOI перед публикацией.")

    article.issue = issue
    article.status = Article.PUBLISHED
    article.published_at = timezone.now()
    article.save(update_fields=["issue", "status", "published_at"])

    # Author + registered co-authors (PRD: "автор и соавторы получают
    # уведомление") — co-authors without a linked account have no way to
    # receive an in-app notification (M3f plan decision #5).
    recipients = {article.submitted_by}
    recipients.update(a.user for a in article.authors.exclude(user=None))

    for user in recipients:
        Notification.objects.create(
            user=user,
            article=article,
            type=Notification.STATUS_CHANGED,
            message=f"Статья «{article.title_ru}» опубликована в выпуске №{issue.number} ({issue.year}). DOI: {article.doi}.",
        )
    return article
