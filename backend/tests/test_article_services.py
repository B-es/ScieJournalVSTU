from __future__ import annotations

import re
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.articles import services
from apps.articles.models import Article, ArticleAuthor, ArticleVersion
from apps.editorial.models import EditorialDecision
from apps.notifications.models import Notification
from apps.reviews.models import Review
from apps.users.models import Role


pytestmark = pytest.mark.django_db


def test_approve_completeness_sets_timestamp_and_creates_decision(article, tech_editor):
    result = services.approve_completeness(article, tech_editor)

    article.refresh_from_db()
    decision = article.decisions.get()
    assert result.id == article.id
    assert article.completeness_approved_at is not None
    assert decision.editor == tech_editor
    assert decision.decision == EditorialDecision.ACCEPT
    assert decision.stage == EditorialDecision.COMPLETENESS_CHECK


def test_return_for_revision_requires_non_blank_comment(article, tech_editor):
    with pytest.raises(ValueError, match="Комментарий обязателен"):
        services.return_for_revision(article, tech_editor, "   ")

    article.refresh_from_db()
    assert article.status == Article.SUBMITTED
    assert not article.decisions.exists()
    assert not article.notifications.exists()


def test_return_for_revision_changes_status_and_notifies_author(article, tech_editor):
    services.return_for_revision(article, tech_editor, "Добавьте справку.")

    article.refresh_from_db()
    decision = article.decisions.get()
    notification = article.notifications.get()
    assert article.status == Article.NEEDS_REVISION
    assert decision.decision == EditorialDecision.REVISE
    assert decision.comment == "Добавьте справку."
    assert notification.user == article.submitted_by
    assert notification.type == Notification.STATUS_CHANGED
    assert "Добавьте справку" in notification.message


def test_approve_and_reject_topic(article, editor):
    services.approve_topic(article, editor)
    assert article.decisions.filter(
        decision=EditorialDecision.ACCEPT,
        stage=EditorialDecision.TOPIC_CHECK,
    ).exists()

    services.reject_topic(article, editor, "Не соответствует тематике.")
    article.refresh_from_db()
    assert article.status == Article.REJECTED
    assert article.decisions.filter(
        decision=EditorialDecision.REJECT,
        stage=EditorialDecision.TOPIC_CHECK,
    ).exists()
    assert article.notifications.filter(user=article.submitted_by).exists()


def test_reject_topic_requires_comment(article, editor):
    with pytest.raises(ValueError, match="Комментарий обязателен"):
        services.reject_topic(article, editor, "")


def test_make_review_decision_rejects_wrong_article_status(article, editor):
    with pytest.raises(ValueError, match="не находится"):
        services.make_review_decision(
            article,
            editor,
            EditorialDecision.ACCEPT,
            "Принять.",
        )


def test_make_review_decision_waits_for_all_accepted_reviews(
    article,
    editor,
    reviewer_factory,
):
    article.status = Article.IN_REVIEW
    article.save(update_fields=["status"])
    Review.objects.create(
        article=article,
        reviewer=reviewer_factory(),
        invitation_status=Review.ACCEPTED,
        deadline=date(2026, 12, 31),
    )

    with pytest.raises(ValueError, match="не все рецензии"):
        services.make_review_decision(
            article,
            editor,
            EditorialDecision.ACCEPT,
            "Принять.",
        )


@pytest.mark.parametrize(
    ("decision", "expected_status"),
    [
        (EditorialDecision.ACCEPT, Article.ACCEPTED),
        (EditorialDecision.REJECT, Article.REJECTED),
        (EditorialDecision.REVISE, Article.NEEDS_REVISION),
    ],
)
def test_make_review_decision_applies_result_and_notifies_author(
    article,
    editor,
    decision,
    expected_status,
):
    article.status = Article.IN_REVIEW
    article.save(update_fields=["status"])

    services.make_review_decision(article, editor, decision, "Итоговое решение")

    article.refresh_from_db()
    assert article.status == expected_status
    assert article.decisions.filter(
        decision=decision,
        stage=EditorialDecision.REVIEW_DECISION,
    ).exists()
    assert article.notifications.filter(
        user=article.submitted_by,
        type=Notification.DECISION_MADE,
    ).exists()


def test_add_revision_creates_next_version_and_documents(article, tech_editor):
    article.status = Article.NEEDS_REVISION
    article.completeness_approved_at = timezone.now()
    article.save(update_fields=["status", "completeness_approved_at"])
    ArticleVersion.objects.create(
        article=article,
        version_number=1,
        manuscript_file=SimpleUploadedFile("v1.pdf", b"v1"),
    )
    EditorialDecision.objects.create(
        article=article,
        editor=tech_editor,
        decision=EditorialDecision.REVISE,
        stage=EditorialDecision.COMPLETENESS_CHECK,
        comment="Исправить.",
    )

    version = services.add_revision_version(
        article,
        SimpleUploadedFile("v2.pdf", b"v2"),
        [SimpleUploadedFile("agreement.pdf", b"agreement")],
        ["Согласие"],
        "Исправлено",
    )

    article.refresh_from_db()
    assert version.version_number == 2
    assert version.author_comment == "Исправлено"
    assert version.documents.get().doc_type == "Согласие"
    assert article.status == Article.SUBMITTED
    assert article.completeness_approved_at is None


def test_add_review_revision_resets_accepted_reviews(
    article,
    editor,
    reviewer_factory,
):
    article.status = Article.NEEDS_REVISION
    article.save(update_fields=["status"])
    EditorialDecision.objects.create(
        article=article,
        editor=editor,
        decision=EditorialDecision.REVISE,
        stage=EditorialDecision.REVIEW_DECISION,
        comment="Повторить рецензирование.",
    )
    reviews = [
        Review.objects.create(
            article=article,
            reviewer=reviewer_factory(),
            invitation_status=Review.ACCEPTED,
            deadline=date(2026, 8, 1),
            recommendation=Review.RECOMMEND_REVISE,
            review_form_data={"commentsForAuthor": "Исправить"},
            submitted_at=timezone.now(),
        )
        for _ in range(2)
    ]

    services.add_revision_version(
        article,
        SimpleUploadedFile("revision.pdf", b"revision"),
        [],
        [],
        "",
    )

    article.refresh_from_db()
    assert article.status == Article.IN_REVIEW
    for review in reviews:
        review.refresh_from_db()
        assert review.invitation_status == Review.ACCEPTED
        assert review.submitted_at is None
        assert review.recommendation == ""
        assert review.review_form_data is None
        assert review.deadline > timezone.now().date()
    assert Notification.objects.filter(
        article=article,
        type=Notification.REVIEWER_INVITED,
    ).count() == 2


def test_assign_doi_requires_accepted_status(article, editor):
    with pytest.raises(ValueError, match="только статье"):
        services.assign_doi(article, editor)


def test_assign_doi_creates_expected_unique_value(article, editor):
    article.status = Article.ACCEPTED
    article.save(update_fields=["status"])

    services.assign_doi(article, editor)

    article.refresh_from_db()
    assert re.fullmatch(r"10\.36622/vstu\.\d{4}\.[0-9a-f]{8}", article.doi)

    with pytest.raises(ValueError, match="уже присвоен"):
        services.assign_doi(article, editor)


def test_publish_requires_accepted_status_and_doi(article, editor, issue):
    with pytest.raises(ValueError, match="только статью"):
        services.publish_article(article, editor, issue)

    article.status = Article.ACCEPTED
    article.save(update_fields=["status"])
    with pytest.raises(ValueError, match="Присвойте DOI"):
        services.publish_article(article, editor, issue)


def test_publish_stamps_issue_and_notifies_author_and_registered_coauthor(
    article,
    editor,
    issue,
    user_factory,
):
    coauthor = user_factory(role=Role.AUTHOR, email="coauthor@example.com")
    ArticleAuthor.objects.create(
        article=article,
        user=coauthor,
        full_name="Соавтор",
        email=coauthor.email,
    )
    ArticleAuthor.objects.create(article=article, full_name="Внешний соавтор")
    article.status = Article.ACCEPTED
    article.doi = "10.36622/vstu.2026.12345678"
    article.save(update_fields=["status", "doi"])

    services.publish_article(article, editor, issue)

    article.refresh_from_db()
    issue.refresh_from_db()
    recipients = set(
        Notification.objects.filter(article=article).values_list("user_id", flat=True)
    )
    assert article.status == Article.PUBLISHED
    assert article.issue == issue
    assert article.published_at is not None
    assert issue.published_at is not None
    assert recipients == {article.submitted_by_id, coauthor.id}
