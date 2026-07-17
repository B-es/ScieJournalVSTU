import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    DS section 6, entity Notification. `type` choices per TS section 9,
    the only place the spec enumerates concrete event types.
    """

    STATUS_CHANGED = "status_changed"
    REVIEWER_INVITED = "reviewer_invited"
    COMMENT_ADDED = "comment_added"
    DECISION_MADE = "decision_made"
    TYPE_CHOICES = [
        (STATUS_CHANGED, "Статус изменён"),
        (REVIEWER_INVITED, "Приглашение рецензенту"),
        (COMMENT_ADDED, "Новый комментарий"),
        (DECISION_MADE, "Решение принято"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    article = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} → {self.user}"
