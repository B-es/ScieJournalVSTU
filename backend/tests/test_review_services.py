from __future__ import annotations

from datetime import date

import pytest

from apps.articles.models import Article, ArticleAuthor
from apps.notifications.models import Notification
from apps.reviews import services
from apps.reviews.models import Review
from apps.users.models import Role


pytestmark = pytest.mark.django_db
DEADLINE = date(2026, 12, 31)


def test_assign_reviewers_rejects_article_author(article, editor):
    with pytest.raises(ValueError, match="Автор статьи"):
        services.assign_reviewers(article, editor, [article.submitted_by_id], DEADLINE)


def test_assign_reviewers_rejects_registered_coauthor(
    article,
    editor,
    reviewer_factory,
):
    coauthor = reviewer_factory()
    ArticleAuthor.objects.create(article=article, user=coauthor, full_name=coauthor.full_name)

    with pytest.raises(ValueError, match="Автор статьи"):
        services.assign_reviewers(article, editor, [coauthor.id], DEADLINE)


def test_assign_reviewers_rejects_user_without_reviewer_role(
    article,
    editor,
    user_factory,
):
    ordinary_user = user_factory()

    with pytest.raises(ValueError, match="не имеют роли"):
        services.assign_reviewers(article, editor, [ordinary_user.id], DEADLINE)


def test_assign_reviewers_creates_reviews_and_notifications(
    article,
    editor,
    reviewer_factory,
):
    reviewers = [reviewer_factory(), reviewer_factory()]

    reviews = services.assign_reviewers(
        article,
        editor,
        [reviewer.id for reviewer in reviewers],
        DEADLINE,
    )

    assert len(reviews) == 2
    assert {review.reviewer_id for review in reviews} == {
        reviewer.id for reviewer in reviewers
    }
    assert all(review.invitation_status == Review.INVITED for review in reviews)
    assert Notification.objects.filter(
        article=article,
        type=Notification.REVIEWER_INVITED,
    ).count() == 2


def test_respond_to_invitation_rejects_wrong_user(review_factory, reviewer_factory):
    review = review_factory()

    with pytest.raises(PermissionError, match="другому пользователю"):
        services.respond_to_invitation(review, True, reviewer_factory())


def test_respond_to_invitation_rejects_second_response(review_factory):
    review = review_factory(invitation_status=Review.ACCEPTED)

    with pytest.raises(ValueError, match="уже дан ответ"):
        services.respond_to_invitation(review, True, review.reviewer)


def test_two_acceptances_start_review_and_cancel_extra_invitation(
    article,
    editor,
    reviewer_factory,
):
    reviewers = [reviewer_factory() for _ in range(3)]
    reviews = services.assign_reviewers(
        article,
        editor,
        [reviewer.id for reviewer in reviewers],
        DEADLINE,
    )

    services.respond_to_invitation(reviews[0], True, reviews[0].reviewer)
    article.refresh_from_db()
    assert article.status == Article.SUBMITTED

    services.respond_to_invitation(reviews[1], True, reviews[1].reviewer)
    article.refresh_from_db()
    reviews[2].refresh_from_db()
    assert article.status == Article.IN_REVIEW
    assert reviews[2].invitation_status == Review.CANCELLED
    assert Notification.objects.filter(
        user=reviews[2].reviewer,
        article=article,
        type=Notification.STATUS_CHANGED,
    ).exists()


def test_decline_notifies_chief_editors(
    review_factory,
    user_factory,
):
    review = review_factory()
    chief_one = user_factory(role=Role.CHIEF_EDITOR)
    chief_two = user_factory(role=Role.CHIEF_EDITOR)

    services.respond_to_invitation(review, False, review.reviewer)

    review.refresh_from_db()
    recipients = set(
        Notification.objects.filter(
            article=review.article,
            type=Notification.STATUS_CHANGED,
        ).values_list("user_id", flat=True)
    )
    assert review.invitation_status == Review.DECLINED
    assert recipients == {chief_one.id, chief_two.id}


def test_reassign_requires_declined_invitation(review_factory, reviewer_factory, editor):
    review = review_factory(invitation_status=Review.INVITED)

    with pytest.raises(ValueError, match="только для отклонённого"):
        services.reassign_reviewer(
            review,
            reviewer_factory().id,
            DEADLINE,
            editor,
        )


def test_reassign_replaces_reviewer_and_sends_invitation(
    review_factory,
    reviewer_factory,
    editor,
):
    review = review_factory(invitation_status=Review.DECLINED)
    replacement = reviewer_factory()

    services.reassign_reviewer(review, replacement.id, DEADLINE, editor)

    review.refresh_from_db()
    assert review.reviewer == replacement
    assert review.invitation_status == Review.INVITED
    assert review.deadline == DEADLINE
    assert Notification.objects.filter(
        user=replacement,
        article=review.article,
        type=Notification.REVIEWER_INVITED,
    ).exists()


def test_submit_review_requires_owner_and_accepted_status(
    review_factory,
    reviewer_factory,
):
    invited_review = review_factory()
    with pytest.raises(PermissionError, match="другому пользователю"):
        services.submit_review(
            invited_review,
            reviewer_factory(),
            Review.RECOMMEND_ACCEPT,
            {"commentsForAuthor": "Хорошо"},
            None,
        )

    with pytest.raises(ValueError, match="после принятия"):
        services.submit_review(
            invited_review,
            invited_review.reviewer,
            Review.RECOMMEND_ACCEPT,
            {"commentsForAuthor": "Хорошо"},
            None,
        )


def test_submit_review_saves_result_and_notifies_chief_only_after_last_review(
    article,
    reviewer_factory,
    user_factory,
):
    chief = user_factory(role=Role.CHIEF_EDITOR)
    reviews = [
        Review.objects.create(
            article=article,
            reviewer=reviewer_factory(),
            invitation_status=Review.ACCEPTED,
            deadline=DEADLINE,
        )
        for _ in range(2)
    ]

    services.submit_review(
        reviews[0],
        reviews[0].reviewer,
        Review.RECOMMEND_ACCEPT,
        {"commentsForAuthor": "Первая рецензия"},
        None,
    )
    assert not Notification.objects.filter(user=chief, article=article).exists()

    services.submit_review(
        reviews[1],
        reviews[1].reviewer,
        Review.RECOMMEND_REVISE,
        {"commentsForAuthor": "Вторая рецензия"},
        None,
    )

    reviews[1].refresh_from_db()
    assert reviews[1].submitted_at is not None
    assert reviews[1].recommendation == Review.RECOMMEND_REVISE
    assert reviews[1].review_form_data["commentsForAuthor"] == "Вторая рецензия"
    assert Notification.objects.filter(
        user=chief,
        article=article,
        type=Notification.STATUS_CHANGED,
    ).exists()


def test_submit_review_cannot_be_repeated(review_factory):
    review = review_factory(invitation_status=Review.ACCEPTED)
    services.submit_review(
        review,
        review.reviewer,
        Review.RECOMMEND_ACCEPT,
        {"commentsForAuthor": "Готово"},
        None,
    )
    review.refresh_from_db()

    with pytest.raises(ValueError, match="уже была отправлена"):
        services.submit_review(
            review,
            review.reviewer,
            Review.RECOMMEND_ACCEPT,
            {"commentsForAuthor": "Повтор"},
            None,
        )
