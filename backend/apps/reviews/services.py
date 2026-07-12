"""Business logic for the reviewer-assignment and response flow (US-4, US-5)."""

from django.db import transaction

from apps.articles.models import Article
from apps.notifications.models import Notification
from apps.users.models import Role, User

from .models import Review


def _article_author_ids(article) -> set:
    ids = {str(article.submitted_by_id)}
    ids.update(str(uid) for uid in article.authors.exclude(user=None).values_list("user_id", flat=True))
    return ids


def assign_reviewers(article, editor, reviewer_ids, deadline) -> list[Review]:
    """
    US-4: assign reviewers (≥2 enforced by ReviewerAssignmentInputSerializer).
    PRD section 7 business rules: no conflict of interest (author != reviewer),
    every id must actually hold the reviewer role.
    """
    reviewer_ids = [str(rid) for rid in reviewer_ids]

    conflicting = _article_author_ids(article) & set(reviewer_ids)
    if conflicting:
        raise ValueError("Автор статьи не может быть назначен её рецензентом.")

    reviewers = list(User.objects.filter(id__in=reviewer_ids, roles__code=Role.REVIEWER).distinct())
    if len(reviewers) != len(set(reviewer_ids)):
        raise ValueError("Один или несколько выбранных пользователей не имеют роли «Рецензент».")

    reviews = []
    with transaction.atomic():
        for reviewer in reviewers:
            review = Review.objects.create(
                article=article, reviewer=reviewer, invitation_status=Review.INVITED, deadline=deadline
            )
            reviews.append(review)
            Notification.objects.create(
                user=reviewer,
                article=article,
                type=Notification.REVIEWER_INVITED,
                message=f"Приглашение на рецензирование статьи «{article.title_ru}» (срок: {deadline}).",
            )
    return reviews


def respond_to_invitation(review: Review, accepted: bool, user) -> Review:
    """US-5: accept/decline. All-accepted -> article moves to in_review (see M3c plan decision #1)."""
    if review.reviewer_id != user.id:
        raise PermissionError("Это приглашение адресовано другому пользователю.")
    if review.invitation_status != Review.INVITED:
        raise ValueError("На это приглашение уже дан ответ.")

    review.invitation_status = Review.ACCEPTED if accepted else Review.DECLINED
    review.save(update_fields=["invitation_status"])

    article = review.article
    if accepted:
        all_accepted = not article.reviews.exclude(invitation_status=Review.ACCEPTED).exists()
        if all_accepted:
            article.status = Article.IN_REVIEW
            article.save(update_fields=["status"])
    else:
        for chief_editor in User.objects.filter(roles__code=Role.CHIEF_EDITOR).distinct():
            Notification.objects.create(
                user=chief_editor,
                article=article,
                type=Notification.STATUS_CHANGED,
                message=(
                    f"Рецензент {user.full_name} отказался от рецензирования статьи "
                    f"«{article.title_ru}» — требуется замена."
                ),
            )

    return review


def reassign_reviewer(review: Review, new_reviewer_id, deadline, editor) -> Review:
    """US-4/US-5: replace a declined reviewer — mutates the existing Review, per TS's /reassign path."""
    if review.invitation_status != Review.DECLINED:
        raise ValueError("Замену можно назначить только для отклонённого приглашения.")

    new_reviewer = User.objects.filter(id=new_reviewer_id, roles__code=Role.REVIEWER).first()
    if new_reviewer is None:
        raise ValueError("Выбранный пользователь не имеет роли «Рецензент».")

    article = review.article
    if str(new_reviewer.id) in _article_author_ids(article):
        raise ValueError("Автор статьи не может быть назначен её рецензентом.")

    review.reviewer = new_reviewer
    review.invitation_status = Review.INVITED
    review.deadline = deadline
    review.save(update_fields=["reviewer", "invitation_status", "deadline"])

    Notification.objects.create(
        user=new_reviewer,
        article=article,
        type=Notification.REVIEWER_INVITED,
        message=f"Приглашение на рецензирование статьи «{article.title_ru}» (срок: {deadline}).",
    )
    return review
