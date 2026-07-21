from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Role
from apps.users.permissions import HasRole

from . import services
from .models import Review
from .serializers import (
    ReassignInputSerializer,
    ReviewListItemSerializer,
    ReviewRespondInputSerializer,
    ReviewSubmitInputSerializer,
)


class MyReviewsView(APIView):
    """
    GET /api/reviews — TS section 7. A reviewer's own invitations; chief
    editors see every invitation across all articles instead (M3c plan
    decision #6 — their "Приглашения" screen needs the full sent list, and
    Review has no per-editor "invited_by" to scope it more narrowly).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.roles.filter(code=Role.CHIEF_EDITOR).exists():
            qs = Review.objects.select_related("reviewer", "article").all()
        else:
            qs = Review.objects.select_related("reviewer", "article").filter(reviewer=request.user)

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(invitation_status=status_filter)

        article_filter = request.query_params.get("article")
        if article_filter:
            qs = qs.filter(article_id=article_filter)

        return Response({"items": ReviewListItemSerializer(qs, many=True).data})


class RespondView(APIView):
    """POST /api/reviews/{id}/respond — TS section 7 (US-5)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)

        input_serializer = ReviewRespondInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            services.respond_to_invitation(review, input_serializer.validated_data["accepted"], request.user)
        except PermissionError as exc:
            return Response({"code": "forbidden", "message": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"code": "invalid_state", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"status": review.invitation_status})


class ReassignView(APIView):
    """POST /api/reviews/{id}/reassign — TS section 7 (US-4/US-5)."""

    permission_classes = [HasRole(Role.CHIEF_EDITOR)]

    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)

        input_serializer = ReassignInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        try:
            services.reassign_reviewer(review, validated["newReviewerId"], validated["deadline"], request.user)
        except ValueError as exc:
            return Response({"code": "invalid_reassignment", "message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"reviewId": str(review.id), "status": review.invitation_status})


class SubmitReviewView(APIView):
    """POST /api/reviews/{id}/submit — TS section 7 (US-6)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)

        input_serializer = ReviewSubmitInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        try:
            services.submit_review(
                review,
                request.user,
                validated["recommendation"],
                validated["formData"],
                validated.get("reviewFile"),
            )
        except PermissionError as exc:
            return Response({"code": "forbidden", "message": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"code": "invalid_state", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"status": "submitted"})
    