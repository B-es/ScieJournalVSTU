import uuid

from django.conf import settings
from django.db import models


class EditorialDecision(models.Model):
    """
    DS section 6, entity EditorialDecision. `stage` distinguishes the
    technical editor's completeness check (US-2, `editor` is the tech editor
    here rather than the chief editor), the preliminary topic-fit check
    (US-4), and the final review-based decision (US-7). Comment is mandatory
    per PRD section 7 business rule, except completeness-check approvals
    (PRD only requires a comment for the *return* case there).
    """

    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"
    DECISION_CHOICES = [
        (ACCEPT, "Принять"),
        (REJECT, "Отклонить"),
        (REVISE, "На доработку"),
    ]

    COMPLETENESS_CHECK = "completeness_check"
    TOPIC_CHECK = "topic_check"
    REVIEW_DECISION = "review_decision"
    STAGE_CHOICES = [
        (COMPLETENESS_CHECK, "Проверка комплектности"),
        (TOPIC_CHECK, "Проверка тематики"),
        (REVIEW_DECISION, "Решение по рецензиям"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey("articles.Article", on_delete=models.CASCADE, related_name="decisions")
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="editorial_decisions")
    decision = models.CharField(max_length=16, choices=DECISION_CHOICES)
    comment = models.TextField()
    stage = models.CharField(max_length=32, choices=STAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "editorial_decisions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.article} — {self.get_decision_display()} ({self.stage})"
