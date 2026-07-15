import json

from rest_framework import serializers

from apps.editorial.models import EditorialDecision
from apps.reviews.models import Review
from apps.reviews.services import MIN_REVIEWERS

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
    """Fills the {reviews: [...]} slot in TS's article-detail response."""

    reviewerId = serializers.UUIDField(source="reviewer_id")
    invitationStatus = serializers.CharField(source="invitation_status")
    submittedAt = serializers.DateTimeField(source="submitted_at")
    # Only this sub-field of review_form_data — never commentsForEditor, and
    # no reviewer identity beyond the opaque id above (PRD section 7: reviews
    # are shown to the author "без раскрытия личности рецензента") — M3e plan
    # decision #5.
    commentsForAuthor = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "reviewerId", "invitationStatus", "deadline", "recommendation", "submittedAt", "commentsForAuthor"]

    def get_commentsForAuthor(self, obj):
        if not obj.review_form_data:
            return ""
        return obj.review_form_data.get("commentsForAuthor", "")


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
    # Exposes the M3b/M3c queue-gating flag so the frontend can tell "awaiting
    # completeness check" apart from "awaiting topic check" — both look like
    # status=submitted with no reviews yet without this (see M3c plan #2).
    completenessApprovedAt = serializers.DateTimeField(source="completeness_approved_at")
    # US-9: set once the article is actually published — see plan decision #1
    # for why this can't just be updated_at.
    publishedAt = serializers.DateTimeField(source="published_at")
    issueId = serializers.UUIDField(source="issue_id", allow_null=True)
    # Raw issueId isn't meaningful to show a user — number/year is what "Выпуск
    # №N" needs. No public issue-detail endpoint exists yet (that's US-10), so
    # exposing it here directly is the cheapest way to make the author's
    # "published" view actually show which issue (M3f plan #6).
    issueNumber = serializers.IntegerField(source="issue.number", default=None)
    issueYear = serializers.IntegerField(source="issue.year", default=None)
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
            "completenessApprovedAt",
            "issueNumber",
            "issueYear",
            "publishedAt",
            "issueId",
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


class CompletenessCheckInputSerializer(serializers.Serializer):
    """POST /api/articles/{id}/completeness-check (TS section 7, US-2)."""

    approved = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs["approved"] and not attrs["comment"].strip():
            raise serializers.ValidationError(
                {"comment": ["Комментарий обязателен при возврате статьи на доработку."]}
            )
        return attrs


class VersionUploadInputSerializer(serializers.Serializer):
    """POST /api/articles/{id}/versions (TS section 7, US-3) — files + comment only, no metadata."""

    manuscriptFile = serializers.FileField()
    authorComment = serializers.CharField(required=False, allow_blank=True, default="")


class TopicCheckInputSerializer(serializers.Serializer):
    """POST /api/articles/{id}/topic-check (TS section 7, US-4)."""

    approved = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs["approved"] and not attrs["comment"].strip():
            raise serializers.ValidationError({"comment": ["Комментарий обязателен при отклонении статьи."]})
        return attrs


class ReviewerAssignmentInputSerializer(serializers.Serializer):
    """POST /api/articles/{id}/reviewers (TS section 7, US-4) — at least 2 reviewers (PRD section 7)."""

    reviewerIds = serializers.ListField(child=serializers.UUIDField(), min_length=MIN_REVIEWERS)
    deadline = serializers.DateField()


class DecisionInputSerializer(serializers.Serializer):
    """
    POST /api/articles/{id}/decision (TS section 7, US-7). Unlike
    topic-check/completeness-check, the comment is mandatory for every
    outcome here — US-7's own wording ("выбирает решение... и указывает
    комментарий") and PRD section 7's general rule both tie the comment to
    "any" chief editor decision, not just the negative one (M3e plan #2).
    """

    decision = serializers.ChoiceField(choices=EditorialDecision.DECISION_CHOICES)
    comment = serializers.CharField()

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError("Комментарий обязателен для любого решения.")
        return value


class PublishInputSerializer(serializers.Serializer):
    """
    POST /api/articles/{id}/publish (TS section 7, US-9). Existence of the
    issue is checked in the view (get_object_or_404) rather than here, so a
    missing issue produces the 404 TS documents for this endpoint instead of
    a generic 400 from field validation.
    """

    issueId = serializers.UUIDField()
