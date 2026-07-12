import json

from rest_framework import serializers

from apps.editorial.models import EditorialDecision
from apps.reviews.models import Review

from .models import Article, ArticleAuthor, ArticleDocument, ArticleVersion


class JSONStringField(serializers.Field):
    """
    Accepts either a native list/dict (JSON request bodies) or a JSON-encoded
    string (multipart request bodies, where structured data has to travel
    alongside file fields — see M3 plan decision #3).
    """

    def to_internal_value(self, data):
        if isinstance(data, (list, dict)):
            return data
        try:
            return json.loads(data)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError("Некорректный JSON.") from exc

    def to_representation(self, value):
        return value


# --- Read serializers -------------------------------------------------

class ArticleAuthorSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name")

    class Meta:
        model = ArticleAuthor
        fields = ["id", "fullName", "affiliation", "email", "order"]


class ArticleDocumentSerializer(serializers.ModelSerializer):
    docType = serializers.CharField(source="doc_type")
    fileUrl = serializers.FileField(source="file", use_url=True)

    class Meta:
        model = ArticleDocument
        fields = ["id", "docType", "fileUrl"]


class ArticleVersionSerializer(serializers.ModelSerializer):
    versionNumber = serializers.IntegerField(source="version_number")
    manuscriptFileUrl = serializers.FileField(source="manuscript_file", use_url=True)
    submittedAt = serializers.DateTimeField(source="submitted_at")
    authorComment = serializers.CharField(source="author_comment")
    documents = ArticleDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ArticleVersion
        fields = ["id", "versionNumber", "manuscriptFileUrl", "submittedAt", "authorComment", "documents"]


class ReviewSerializer(serializers.ModelSerializer):
    """Minimal — the review module itself doesn't exist yet, this just fills the {reviews: [...]} slot in TS's detail response."""

    reviewerId = serializers.UUIDField(source="reviewer_id")
    invitationStatus = serializers.CharField(source="invitation_status")
    submittedAt = serializers.DateTimeField(source="submitted_at")

    class Meta:
        model = Review
        fields = ["id", "reviewerId", "invitationStatus", "deadline", "recommendation", "submittedAt"]


class EditorialDecisionSerializer(serializers.ModelSerializer):
    """Minimal — same rationale as ReviewSerializer, for the {decisions: [...]} slot."""

    editorId = serializers.UUIDField(source="editor_id")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = EditorialDecision
        fields = ["id", "editorId", "decision", "comment", "stage", "createdAt"]


class ArticleListSerializer(serializers.ModelSerializer):
    titleRu = serializers.CharField(source="title_ru")
    titleEn = serializers.CharField(source="title_en")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = Article
        fields = ["id", "titleRu", "titleEn", "status", "topic", "createdAt", "updatedAt"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializes the `article` key of GET /api/articles/{id}'s
    {article, versions, reviews, decisions} envelope (TS section 7) — the
    latter three are siblings assembled by the view, not nested here.
    """

    titleRu = serializers.CharField(source="title_ru")
    titleEn = serializers.CharField(source="title_en")
    abstractRu = serializers.CharField(source="abstract_ru")
    abstractEn = serializers.CharField(source="abstract_en")
    keywordsRu = serializers.ListField(source="keywords_ru", child=serializers.CharField())
    keywordsEn = serializers.ListField(source="keywords_en", child=serializers.CharField())
    pagesCount = serializers.IntegerField(source="pages_count")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    lastAutosavedAt = serializers.DateTimeField(source="last_autosaved_at")
    authors = ArticleAuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "titleRu",
            "titleEn",
            "abstractRu",
            "abstractEn",
            "keywordsRu",
            "keywordsEn",
            "topic",
            "status",
            "doi",
            "pagesCount",
            "createdAt",
            "updatedAt",
            "lastAutosavedAt",
            "authors",
        ]


# --- Write input (draft save / submit) ---------------------------------

class ArticleDraftInputSerializer(serializers.Serializer):
    """
    Validates the raw multipart body shared by POST /api/articles/draft and
    POST /api/articles/{id}/submit (TS section 7) — every field optional,
    since draft saves may carry only a subset (M3 plan decisions #1-#3).
    `documents`/`documentTypes` are read directly from request.FILES /
    request.data by the view rather than through this serializer — see plan.
    """

    articleId = serializers.UUIDField(required=False, allow_null=True)
    titleRu = serializers.CharField(required=False, allow_blank=True)
    titleEn = serializers.CharField(required=False, allow_blank=True)
    abstractRu = serializers.CharField(required=False, allow_blank=True)
    abstractEn = serializers.CharField(required=False, allow_blank=True)
    keywordsRu = JSONStringField(required=False)
    keywordsEn = JSONStringField(required=False)
    topic = serializers.CharField(required=False, allow_blank=True)
    authors = JSONStringField(required=False)
    manuscriptFile = serializers.FileField(required=False)
