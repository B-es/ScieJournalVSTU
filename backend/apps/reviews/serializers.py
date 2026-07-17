from rest_framework import serializers

from apps.articles.models import Article
from apps.articles.serializers import JSONStringField

from .models import Review


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

    def validate_formData(self, value):
        if not isinstance(value, dict) or not str(value.get("commentsForAuthor", "")).strip():
            raise serializers.ValidationError("Заполните комментарии для автора.")
        return value
