from rest_framework import serializers

from apps.articles.models import Article
from apps.articles.serializers import JSONStringField

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Fills the {reviews: [...]} slot in TS's article-detail response."""
    
    reviewerId = serializers.UUIDField(source="reviewer_id")
    invitationStatus = serializers.CharField(source="invitation_status")
    submittedAt = serializers.DateTimeField(source="submitted_at")
    
    commentsForAuthor = serializers.SerializerMethodField()
    
    reviewFileUrl = serializers.SerializerMethodField()
    reviewFileName = serializers.SerializerMethodField()
    
    evaluationRating = serializers.JSONField(source="evaluation_rating", read_only=True)
    languageQuality = serializers.CharField(source="language_quality", read_only=True)
    conflictOfInterest = serializers.BooleanField(source="conflict_of_interest", read_only=True)
    plagiarismDetected = serializers.BooleanField(source="plagiarism_detected", read_only=True)
    ethicalIssues = serializers.BooleanField(source="ethical_issues", read_only=True)
    articleRating = serializers.JSONField(source="article_rating", read_only=True)
    
    class Meta:
        model = Review
        fields = [
            "id", 
            "reviewerId", 
            "invitationStatus", 
            "deadline", 
            "recommendation", 
            "submittedAt", 
            "commentsForAuthor", 
            "reviewFileUrl", 
            "reviewFileName",
            "evaluationRating",
            "languageQuality",
            "conflictOfInterest",
            "plagiarismDetected",
            "ethicalIssues",
            "articleRating"
        ]
    
    def get_commentsForAuthor(self, obj):
        if not obj.review_form_data:
            return ""
        return obj.review_form_data.get("commentsForAuthor", "")
    
    def get_reviewFileUrl(self, obj):
        if obj.review_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.review_file.url)
            return obj.review_file.url
        return None
    
    def get_reviewFileName(self, obj):
        if obj.review_file:
            return obj.review_file.name.split('/')[-1]
        return None

class ReviewArticleSummarySerializer(serializers.ModelSerializer):
    """Just enough article info for an invitation card (DS section 4) — no manuscript access here (US-6)."""

    titleRu = serializers.CharField(source="title_ru")
    titleEn = serializers.CharField(source="title_en")
    abstractRu = serializers.CharField(source="abstract_ru")

    class Meta:
        model = Article
        fields = ["id", "titleRu", "titleEn", "abstractRu", "topic"]


class ReviewListItemSerializer(serializers.ModelSerializer):
    """
    GET /api/reviews (TS section 7, US-5) — a reviewer's own invitations, or
    (chief editor) all of them. Reviewer identity is fine to expose here
    (unlike ReviewSerializer on the article-detail endpoint, which authors
    can also see): this endpoint is reviewer/chief-editor only, and the chief
    editor's invitations screen needs the email to tell invitees apart.
    """

    article = ReviewArticleSummarySerializer(read_only=True)
    reviewerId = serializers.UUIDField(source="reviewer_id", read_only=True)
    reviewerFullName = serializers.CharField(source="reviewer.full_name", read_only=True)
    reviewerEmail = serializers.CharField(source="reviewer.email", read_only=True)
    invitationStatus = serializers.CharField(source="invitation_status")
    submittedAt = serializers.DateTimeField(source="submitted_at", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "article",
            "reviewerId",
            "reviewerFullName",
            "reviewerEmail",
            "invitationStatus",
            "deadline",
            "recommendation",
            "submittedAt",
        ]


class ReviewRespondInputSerializer(serializers.Serializer):
    """POST /api/reviews/{id}/respond (TS section 7, US-5)."""

    accepted = serializers.BooleanField()


class ReassignInputSerializer(serializers.Serializer):
    """POST /api/reviews/{id}/reassign (TS section 7, US-4/US-5)."""

    newReviewerId = serializers.UUIDField()
    deadline = serializers.DateField()


class ReviewSubmitInputSerializer(serializers.Serializer):
    """
    POST /api/reviews/{id}/submit (TS section 7, US-6). `formData` is the
    reviewer's questionnaire — TS/DS only call it "анкета рецензента" without
    a fixed schema, so it's two free-form fields (M3d plan decision #2):
    commentsForAuthor (required — the actual substance of the review) and
    commentsForEditor (optional, confidential).
    """

    recommendation = serializers.ChoiceField(choices=Review.RECOMMENDATION_CHOICES)
    formData = JSONStringField()
    reviewFile = serializers.FileField(required=False)
    
    evaluationRating = JSONStringField(required=False, default=dict)
    languageQuality = serializers.CharField(required=False, allow_blank=True, default="")
    conflictOfInterest = serializers.BooleanField(required=False, allow_null=True, default=None)
    plagiarismDetected = serializers.BooleanField(required=False, allow_null=True, default=None)
    ethicalIssues = serializers.BooleanField(required=False, allow_null=True, default=None)
    articleRating = JSONStringField(required=False, default=dict)

    def validate_formData(self, value):
        if not isinstance(value, dict) or not str(value.get("commentsForAuthor", "")).strip():
            raise serializers.ValidationError("Заполните комментарии для автора.")
        return value
    
    def validate_evaluationRating(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Оценка должна быть объектом JSON.")
        allowed = {"yes", "improve", "required", "na"}
        for k, v in value.items():
            if v not in allowed:
                raise serializers.ValidationError(f"Недопустимое значение для {k}: {v}")
        return value
    
    def validate_articleRating(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Рейтинг должен быть объектом JSON.")
        allowed = {"high", "medium", "low", "no_answer"}
        for k, v in value.items():
            if v not in allowed:
                raise serializers.ValidationError(f"Недопустимое значение для {k}: {v}")
        return value