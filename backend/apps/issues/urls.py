from django.urls import path

from .views import IssueCreateView

urlpatterns = [
    path("", IssueCreateView.as_view(), name="issue-create"),
]
