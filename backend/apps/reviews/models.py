import uuid

from django.conf import settings
from django.db import models


def review_upload_path(instance, filename):
    return f"reviews/{instance.article_id}/{instance.id}/{filename}"


class Review(models.Model):
    """DS section 6, entity Review — combines the invitation and the review itself."""

    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    INVITATION_STATUS_CHOICES = [
        (INVITED, "Приглашён"),
        (ACCEPTED, "Принято"),
        (DECLINED, "Отклонено"),
    ]

    RECOMMEND_ACCEPT = "accept"
    RECOMMEND_REVISE = "revise"
    RECOMMEND_REJECT = "reject"
    RECOMMENDATION_CHOICES = [
        (RECOMMEND_ACCEPT, "Принять"),
        (RECOMMEND_REVISE, "На доработку"),
        (RECOMMEND_REJECT, "Отклонить"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey("articles.Article", on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reviews")

    invitation_status = models.CharField(max_length=16, choices=INVITATION_STATUS_CHOICES, default=INVITED)
    deadline = models.DateField()

    recommendation = models.CharField(max_length=16, choices=RECOMMENDATION_CHOICES, blank=True)
    review_form_data = models.JSONField(null=True, blank=True)
    review_file = models.FileField(upload_to=review_upload_path, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-deadline"]

    def __str__(self):
        return f"{self.article} — {self.reviewer}"
