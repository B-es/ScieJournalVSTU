from django.urls import path

from .views import ArticleDetailView, ArticleDraftView, ArticleListView, ArticleSubmitView

urlpatterns = [
    path("draft", ArticleDraftView.as_view(), name="article-draft"),
    path("", ArticleListView.as_view(), name="article-list"),
    path("<uuid:article_id>", ArticleDetailView.as_view(), name="article-detail"),
    path("<uuid:article_id>/submit", ArticleSubmitView.as_view(), name="article-submit"),
]
