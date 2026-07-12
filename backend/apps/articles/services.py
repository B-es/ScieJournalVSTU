"""
Business logic shared between the Django Admin actions (the actual
human-facing UI for the technical editor — see M3b plan decision #1) and the
REST endpoints documented in TS section 7 (decision #2): one implementation,
two entry points.
"""

from django.db.models import Max
from django.utils import timezone

from apps.editorial.models import EditorialDecision
from apps.notifications.models import Notification

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


def add_revision_version(
    article: Article,
    manuscript_file,
    documents_files,
    document_types,
    author_comment: str,
) -> ArticleVersion:
    """US-3: author uploads a corrected version after a completeness-check return."""
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
    # back from. The only source of needs_revision right now is the
    # completeness check, so this always goes back to the tech-editor queue.
    # Once the review-decision revision cycle (US-7/8) exists, branch here on
    # the most recent EditorialDecision's stage instead of hardcoding.
    article.status = Article.SUBMITTED
    article.completeness_approved_at = None
    article.save(update_fields=["status", "completeness_approved_at"])

    return version
