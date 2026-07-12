import uuid

from django.conf import settings
from django.db import models


def manuscript_upload_path(instance, filename):
    return f"articles/{instance.article_id}/versions/{instance.version_number}/{filename}"


def document_upload_path(instance, filename):
    return f"articles/{instance.article_version.article_id}/documents/{filename}"


class Article(models.Model):
    """DS section 6, entity Article. Status model per PRD section 5."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    PUBLISHED = "published"

    STATUS_CHOICES = [
        (DRAFT, "Черновик"),
        (SUBMITTED, "На рассмотрении"),
        (NEEDS_REVISION, "Требуется доработка"),
        (REJECTED, "Отклонена"),
        (IN_REVIEW, "Рецензируется"),
        (ACCEPTED, "Принята к публикации"),
        (PUBLISHED, "Опубликована"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title_ru = models.CharField(max_length=512)
    title_en = models.CharField(max_length=512)
    abstract_ru = models.TextField()
    abstract_en = models.TextField()
    # JSONField (list[str]) instead of Postgres ArrayField — keeps SQLite dev usable (see TS section 2).
    keywords_ru = models.JSONField(default=list, blank=True)
    keywords_en = models.JSONField(default=list, blank=True)
    topic = models.CharField(max_length=255)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=DRAFT)

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_articles"
    )
    doi = models.CharField(max_length=128, blank=True)
    pages_count = models.PositiveIntegerField(null=True, blank=True)
    issue = models.ForeignKey(
        "issues.Issue", on_delete=models.SET_NULL, null=True, blank=True, related_name="articles"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_autosaved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "articles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title_ru


class ArticleAuthor(models.Model):
    """DS section 6, entity ArticleAuthor (co-authors, may be unregistered)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="authors")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="co_authored_articles"
    )
    full_name = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "article_authors"
        ordering = ["order"]

    def __str__(self):
        return self.full_name


class ArticleVersion(models.Model):
    """DS section 6, entity ArticleVersion (manuscript version history)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    manuscript_file = models.FileField(upload_to=manuscript_upload_path)
    submitted_at = models.DateTimeField(auto_now_add=True)
    author_comment = models.TextField(blank=True)

    class Meta:
        db_table = "article_versions"
        ordering = ["version_number"]
        unique_together = ("article", "version_number")

    def __str__(self):
        return f"{self.article} v{self.version_number}"


class ArticleDocument(models.Model):
    """
    DS section 6, entity ArticleDocument (supporting documents per version).
    doc_type is a free-form CharField, not a fixed choices enum: TS explicitly
    marks the document type list as "уточняется отдельно" (undecided) — see
    plan notes for M1.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article_version = models.ForeignKey(ArticleVersion, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=128)
    file = models.FileField(upload_to=document_upload_path)

    class Meta:
        db_table = "article_documents"

    def __str__(self):
        return f"{self.doc_type} ({self.article_version})"
