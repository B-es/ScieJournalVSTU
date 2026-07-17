from django.urls import path

from .views import NotificationReadView, NotificationsListView

urlpatterns = [
    path("", NotificationsListView.as_view(), name="notification-list"),
    path(
        "<uuid:notification_id>/read",
        NotificationReadView.as_view(),
        name="notification-read",
    ),
]
