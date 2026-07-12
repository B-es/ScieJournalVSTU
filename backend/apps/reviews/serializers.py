from rest_framework import serializers

from apps.articles.models import Article

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
    """GET /api/reviews (TS section 7, US-5) — a reviewer's own invitations, or (chief editor) all of them."""

    article = ReviewArticleSummarySerializer(read_only=True)
    reviewerId = serializers.UUIDField(source="reviewer_id", read_only=True)
    invitationStatus = serializers.CharField(source="invitation_status")
    submittedAt = serializers.DateTimeField(source="submitted_at", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "article", "reviewerId", "invitationStatus", "deadline", "recommendation", "submittedAt"]


class ReviewRespondInputSerializer(serializers.Serializer):
    """POST /api/reviews/{id}/respond (TS section 7, US-5)."""

    accepted = serializers.BooleanField()


class ReassignInputSerializer(serializers.Serializer):
    """POST /api/reviews/{id}/reassign (TS section 7, US-4/US-5)."""

    newReviewerId = serializers.UUIDField()
    deadline = serializers.DateField()
