import uuid

from django.db import models

_SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class JournalSettings(models.Model):
    """DS section 6, entity JournalSettings — singleton record, managed via Django Admin."""

    id = models.UUIDField(primary_key=True, default=_SINGLETON_ID, editable=False)
    journal_name_ru = models.CharField(max_length=255)
    journal_name_en = models.CharField(max_length=255)
    issn = models.CharField(max_length=16, blank=True)
    about_ru = models.TextField()
    about_en = models.TextField()
    # Expected shape (no schema enforced — edited as raw JSON in Django Admin):
    # [{"fullNameRu": "...", "fullNameEn": "...", "roleRu": "...", "roleEn": "...",
    #   "affiliationRu": "...", "affiliationEn": "...", "order": 0}, ...]
    editorial_board = models.JSONField(null=True, blank=True)
    # M5: "Требования к авторам" page content — no dedicated model/US for this
    # page (see M5 plan #2), just static editorial text on the same singleton.
    guidelines_for_authors_ru = models.TextField(blank=True)
    guidelines_for_authors_en = models.TextField(blank=True)

    class Meta:
        db_table = "journal_settings"
        verbose_name = "Journal settings"
        verbose_name_plural = "Journal settings"

    def __str__(self):
        return self.journal_name_ru

    def save(self, *args, **kwargs):
        self.id = _SINGLETON_ID
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            id=_SINGLETON_ID,
            defaults={
                "journal_name_ru": "Научный журнал ВолгГТУ",
                "journal_name_en": "VSTU Scientific Journal",
                "about_ru": "",
                "about_en": "",
            },
        )
        return obj
