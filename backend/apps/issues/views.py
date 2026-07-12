from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Role
from apps.users.permissions import HasRole

from .models import Issue
from .serializers import IssueCreateInputSerializer


class IssueCreateView(APIView):
    """POST /api/issues — TS section 7 (US-9)."""

    permission_classes = [HasRole(Role.TECH_EDITOR)]

    def post(self, request):
        input_serializer = IssueCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        issue = Issue.objects.create(
            number=validated["number"],
            year=validated["year"],
            description_ru=validated["descriptionRu"],
            description_en=validated["descriptionEn"],
            cover_image=validated.get("coverImage"),
        )

        return Response({"issueId": str(issue.id)}, status=status.HTTP_201_CREATED)
