from rest_framework import serializers

from .models import Notification


class NotificationListItemSerializer(serializers.ModelSerializer):
    """
    GET /api/reviews — item shape.camelCase keys per TS section 4.
    """

    articleId = serializers.UUIDField(source="article_id", allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at")
    isRead = serializers.BooleanField(source="is_read")

    class Meta:
        model = Notification
        fields = ["id", "type", "message", "isRead", "articleId", "createdAt"]
