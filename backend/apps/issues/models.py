import uuid

from django.db import models


def cover_upload_path(instance, filename):
    return f"issues/{instance.id}/{filename}"


class Issue(models.Model):
    """DS section 6, entity Issue (журнал выпуск)."""

    LANGUAGE_CHOICES = [
        ("ru", "Русский"),
        ("en", "English"),
        ("mixed", "Смешанный"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to=cover_upload_path, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default="mixed")

    class Meta:
        db_table = "issues"
        ordering = ["-year", "-number"]
        unique_together = ("number", "year")

    def __str__(self):
        return f"№{self.number} ({self.year})"
