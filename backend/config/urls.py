"""
URL configuration. API routes are namespaced under /api/ per TS section 7.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.users.views import ReviewersListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/users/reviewers", ReviewersListView.as_view(), name="users-reviewers"),
    path("api/articles/", include("apps.articles.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/issues/", include("apps.issues.urls")),
    path("api/public/", include("apps.public.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
