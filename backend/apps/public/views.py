from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.articles.models import Article
from apps.issues.models import Issue
from apps.journal_settings.models import JournalSettings

from . import services
from .serializers import (
    PublicArticleDetailSerializer,
    PublicArticleListSerializer,
    PublicIssueListSerializer,
    PublicJournalSettingsSerializer,
)

DEFAULT_PAGE_SIZE = 20


def _paginate(qs, request):
    """
    US-10: no DRF pagination class is configured anywhere in this project
    (see M4 plan decision #4) — hand-rolled page/pageSize, same manual style
    as the existing `?status=` filter in ArticleListView.
    """
    try:
        page = max(int(request.query_params.get("page", 1)), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.query_params.get("pageSize", DEFAULT_PAGE_SIZE)), 1), 100)
    except ValueError:
        page_size = DEFAULT_PAGE_SIZE

    total = qs.count()
    start = (page - 1) * page_size
    return qs[start : start + page_size], total


class PublicArticleListView(APIView):
    """GET /api/public/articles — US-10 search/archive listing. Published articles only."""

    permission_classes = [AllowAny]

    def get(self, request):
        qs = Article.objects.filter(status=Article.PUBLISHED)

        q = request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(title_ru__icontains=q)
                | Q(title_en__icontains=q)
                | Q(topic__icontains=q)
                | Q(keywords_ru__icontains=q)
                | Q(keywords_en__icontains=q)
                | Q(authors__full_name__icontains=q)
            ).distinct()

        keyword = request.query_params.get("keyword")
        if keyword:
            qs = qs.filter(Q(keywords_ru__icontains=keyword) | Q(keywords_en__icontains=keyword)).distinct()

        author = request.query_params.get("author")
        if author:
            qs = qs.filter(authors__full_name__icontains=author).distinct()

        topic = request.query_params.get("topic")
        if topic:
            qs = qs.filter(topic__icontains=topic)

        date_from = request.query_params.get("dateFrom")
        if date_from:
            qs = qs.filter(published_at__date__gte=date_from)
        date_to = request.query_params.get("dateTo")
        if date_to:
            qs = qs.filter(published_at__date__lte=date_to)

        qs = qs.order_by("-published_at")
        page_items, total = _paginate(qs, request)
        return Response({"items": PublicArticleListSerializer(page_items, many=True).data, "total": total})


class PublicArticleDetailView(APIView):
    """GET /api/public/articles/{id} — US-10 article page: {article, pdfUrl}."""

    permission_classes = [AllowAny]

    def get(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id, status=Article.PUBLISHED)
        latest_version = article.versions.order_by("-version_number").first()
        pdf_url = None
        if latest_version and latest_version.manuscript_file:
            pdf_url = request.build_absolute_uri(latest_version.manuscript_file.url)
        return Response({"article": PublicArticleDetailSerializer(article).data, "pdfUrl": pdf_url})


class PublicIssueListView(APIView):
    """GET /api/public/issues — US-10 archive. Published issues only, optional ?year=."""

    permission_classes = [AllowAny]

    def get(self, request):
        qs = Issue.objects.filter(published_at__isnull=False)
        year = request.query_params.get("year")
        if year:
            qs = qs.filter(year=year)
        return Response({"items": PublicIssueListSerializer(qs, many=True, context={"request": request}).data})


class PublicIssueDetailView(APIView):
    """GET /api/public/issues/{id} — US-10 issue page: {issue, articles} (TS section 7)."""

    permission_classes = [AllowAny]

    def get(self, request, issue_id):
        issue = get_object_or_404(Issue, pk=issue_id, published_at__isnull=False)
        articles = issue.articles.filter(status=Article.PUBLISHED).order_by("title_ru")
        return Response(
            {
                "issue": PublicIssueListSerializer(issue, context={"request": request}).data,
                "articles": PublicArticleListSerializer(articles, many=True).data,
            }
        )


class ArticleCitationView(APIView):
    """GET /api/public/articles/{id}/citation — US-12."""

    permission_classes = [AllowAny]

    def get(self, request, article_id):
        fmt = request.query_params.get("format")
        if fmt not in services.FORMATS:
            return Response(
                {"code": "invalid_format", "message": "Формат должен быть одним из: gost, apa, bibtex."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        article = get_object_or_404(Article, pk=article_id, status=Article.PUBLISHED)
        try:
            citation_text = services.build_citation(article, fmt)
        except ValueError as exc:
            return Response({"code": "no_doi", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"format": fmt, "citationText": citation_text})


class PublicJournalSettingsView(APIView):
    """GET /api/public/settings — M5: backs "О журнале"/"Требования к авторам"."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(PublicJournalSettingsSerializer(JournalSettings.load()).data)
