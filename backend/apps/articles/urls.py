from django.urls import path

from .views import (
    ArticleAssignDoiView,
    ArticleCompletenessCheckView,
    ArticleDecisionView,
    ArticleDetailView,
    ArticleDraftView,
    ArticleListView,
    ArticlePublishView,
    ArticleReviewersView,
    ArticleSubmitView,
    ArticleTopicCheckView,
    ArticleVersionsView,
)

urlpatterns = [
    path("draft", ArticleDraftView.as_view(), name="article-draft"),
    path("", ArticleListView.as_view(), name="article-list"),
    path("<uuid:article_id>", ArticleDetailView.as_view(), name="article-detail"),
    path("<uuid:article_id>/submit", ArticleSubmitView.as_view(), name="article-submit"),
    path("<uuid:article_id>/versions", ArticleVersionsView.as_view(), name="article-versions"),
    path(
        "<uuid:article_id>/completeness-check",
        ArticleCompletenessCheckView.as_view(),
        name="article-completeness-check",
    ),
    path("<uuid:article_id>/topic-check", ArticleTopicCheckView.as_view(), name="article-topic-check"),
    path("<uuid:article_id>/reviewers", ArticleReviewersView.as_view(), name="article-reviewers"),
    path("<uuid:article_id>/decision", ArticleDecisionView.as_view(), name="article-decision"),
    path("<uuid:article_id>/doi", ArticleAssignDoiView.as_view(), name="article-doi"),
    path("<uuid:article_id>/publish", ArticlePublishView.as_view(), name="article-publish"),
]
