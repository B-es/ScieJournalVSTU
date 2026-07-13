from django.urls import path

from .views import (
    ArticleCitationView,
    PublicArticleDetailView,
    PublicArticleListView,
    PublicIssueDetailView,
    PublicIssueListView,
)

urlpatterns = [
    path("articles", PublicArticleListView.as_view(), name="public-article-list"),
    path("articles/<uuid:article_id>", PublicArticleDetailView.as_view(), name="public-article-detail"),
    path("articles/<uuid:article_id>/citation", ArticleCitationView.as_view(), name="public-article-citation"),
    path("issues", PublicIssueListView.as_view(), name="public-issue-list"),
    path("issues/<uuid:issue_id>", PublicIssueDetailView.as_view(), name="public-issue-detail"),
]
