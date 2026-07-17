from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationListItemSerializer


class NotificationsListView(APIView):
    """
    GET /api/notifications — TS section 7.
    Returns the current user's notifications, newest first.
    Optional query params:
      - is_read: "true" | "false"
      - type: one of Notification.TYPE_CHOICES keys
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)

        is_read_param = request.query_params.get("is_read")
        if is_read_param is not None:
            qs = qs.filter(is_read=is_read_param.lower() == "true")

        type_param = request.query_params.get("type")
        if type_param:
            qs = qs.filter(type=type_param)

        return Response({"items": NotificationListItemSerializer(qs, many=True).data})


class NotificationReadView(APIView):
    """
    PATCH /api/notifications/{id}/read — TS section 7 (US-10 area).
    Marks a single notification as read. Only the owner may mutate it.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id)

        if notification.user_id != request.user.id:
            return Response(
                {"code": "forbidden", "message": "Not your notification"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        return Response({"status": "ok"})
