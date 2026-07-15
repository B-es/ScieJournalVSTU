import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.users.models import Role, User
from apps.users.permissions import HasRole

from apps.issues.models import Issue
from apps.reviews import services as review_services
from apps.reviews.models import Review

from . import services
from .models import Article, ArticleAuthor, ArticleVersion
from .serializers import (
    ArticleDetailSerializer,
    ArticleDraftInputSerializer,
    ArticleListSerializer,
    ArticleVersionSerializer,
    CompletenessCheckInputSerializer,
    DecisionInputSerializer,
    EditorialDecisionSerializer,
    PublishInputSerializer,
    ReviewerAssignmentInputSerializer,
    ReviewSerializer,
    TopicCheckInputSerializer,
    VersionUploadInputSerializer,
)
from .validators import validate_manuscript_file

FIELD_MAP = {
    "titleRu": "title_ru",
    "titleEn": "title_en",
    "abstractRu": "abstract_ru",
    "abstractEn": "abstract_en",
    "keywordsRu": "keywords_ru",
    "keywordsEn": "keywords_en",
    "topic": "topic",
}


def _get_owned_article_or_404(article_id, user):
    article = get_object_or_404(Article, pk=article_id)
    if article.submitted_by_id != user.id:
        raise PermissionDenied("Эта статья вам не принадлежит.")
    return article


def _get_visible_article_or_404(article_id, user):
    """
    Read access for GET /api/articles/{id} — broader than the author-only
    write gate above (M3c plan decision #6): the submitting author, any
    chief editor, or a reviewer who has *accepted* their invitation (PRD
    section 7: full-text access opens only after explicit acceptance).
    """
    article = get_object_or_404(Article, pk=article_id)
    if article.submitted_by_id == user.id:
        return article
    if user.roles.filter(code=Role.CHIEF_EDITOR).exists():
        return article
    if article.reviews.filter(reviewer=user, invitation_status=Review.ACCEPTED).exists():
        return article
    raise PermissionDenied("У вас нет доступа к этой статье.")


def _apply_authors(article, authors_data):
    """Draft/submit always sends the full current author list — replace, not diff (see plan)."""
    if authors_data is None:
        return
    article.authors.all().delete()
    for idx, author in enumerate(authors_data):
        ArticleAuthor.objects.create(
            article=article,
            full_name=author.get("fullName", ""),
            affiliation=author.get("affiliation", ""),
            email=author.get("email", ""),
            order=idx,
        )


def _apply_manuscript(article, manuscript_file):
    if manuscript_file is None:
        return
    version, _ = ArticleVersion.objects.get_or_create(article=article, version_number=1)
    version.manuscript_file = manuscript_file
    version.save()


def _apply_documents(article, files, doc_types):
    if not files:
        return
    version, _ = ArticleVersion.objects.get_or_create(article=article, version_number=1)
    for idx, file in enumerate(files):
        doc_type = doc_types[idx] if doc_types and idx < len(doc_types) else ""
        version.documents.create(doc_type=doc_type, file=file)


def _parse_document_types(raw):
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


def _apply_request_to_article(article, request):
    """Shared by draft-save and submit: validates the optional field set and mutates `article` + related rows."""
    input_serializer = ArticleDraftInputSerializer(data=request.data)
    input_serializer.is_valid(raise_exception=True)
    validated = input_serializer.validated_data

    for camel, snake in FIELD_MAP.items():
        if camel in validated:
            setattr(article, snake, validated[camel])

    article.save()

    if "authors" in validated:
        _apply_authors(article, validated["authors"])

    if "manuscriptFile" in validated:
        _apply_manuscript(article, validated["manuscriptFile"])

    doc_files = request.FILES.getlist("documents")
    doc_types = _parse_document_types(request.data.get("documentTypes"))
    _apply_documents(article, doc_files, doc_types)


def _completeness_errors(article):
    errors = {}

    def require(field, camel_name):
        value = getattr(article, field)
        if not value:
            errors[camel_name] = ["Обязательное поле"]

    require("title_ru", "titleRu")
    require("title_en", "titleEn")
    require("abstract_ru", "abstractRu")
    require("abstract_en", "abstractEn")
    require("keywords_ru", "keywordsRu")
    require("keywords_en", "keywordsEn")
    require("topic", "topic")

    if not article.authors.exists():
        errors["authors"] = ["Укажите хотя бы одного автора"]

    version = article.versions.filter(version_number=1).first()
    if not version or not version.manuscript_file:
        errors["manuscriptFile"] = ["Прикрепите файл рукописи"]
    else:
        try:
            validate_manuscript_file(version.manuscript_file)
        except serializers.ValidationError as exc:
            errors["manuscriptFile"] = [str(exc.detail[0])]

    return errors


class ArticleDraftView(APIView):
    """POST /api/articles/draft — TS section 7 (US-1, US-11). Create-or-update by optional articleId."""

    permission_classes = [HasRole(Role.AUTHOR)]

    def post(self, request):
        article_id = request.data.get("articleId") or None
        if article_id:
            article = _get_owned_article_or_404(article_id, request.user)
            if article.status != Article.DRAFT:
                return Response(
                    {"code": "not_a_draft", "message": "Статья больше не является черновиком."},
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            article = Article(submitted_by=request.user, status=Article.DRAFT)
            article.save()

        _apply_request_to_article(article, request)
        article.last_autosaved_at = timezone.now()
        article.save(update_fields=["last_autosaved_at"])

        return Response(
            {"articleId": str(article.id), "status": article.status, "lastAutosavedAt": article.last_autosaved_at}
        )


class ArticleSubmitView(APIView):
    """POST /api/articles/{id}/submit — TS section 7 (US-1). Merges any provided fields, then validates completeness."""

    permission_classes = [HasRole(Role.AUTHOR)]

    def post(self, request, article_id):
        article = _get_owned_article_or_404(article_id, request.user)
        if article.status != Article.DRAFT:
            return Response(
                {"code": "not_a_draft", "message": "Статья уже отправлена или обрабатывается."},
                status=status.HTTP_409_CONFLICT,
            )

        _apply_request_to_article(article, request)

        errors = _completeness_errors(article)
        if errors:
            return Response(
                {
                    "code": "incomplete_article",
                    "message": "Заполните обязательные поля перед отправкой.",
                    "fieldErrors": errors,
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        article.status = Article.SUBMITTED
        article.save(update_fields=["status"])

        for tech_editor in User.objects.filter(roles__code=Role.TECH_EDITOR).distinct():
            Notification.objects.create(
                user=tech_editor,
                article=article,
                type=Notification.STATUS_CHANGED,
                message=f"Новая статья на проверку комплектности: «{article.title_ru}».",
            )

        return Response({"articleId": str(article.id), "status": article.status})


class ArticleCompletenessCheckView(APIView):
    """
    POST /api/articles/{id}/completeness-check — TS section 7 (US-2).
    Human-facing workflow is Django Admin (see plan decision #1); this
    endpoint exists because TS documents it explicitly and shares the same
    apps.articles.services functions the admin actions use.
    """

    permission_classes = [HasRole(Role.TECH_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        if article.status != Article.SUBMITTED or article.completeness_approved_at is not None:
            return Response(
                {"code": "not_in_queue", "message": "Статья не находится в очереди проверки комплектности."},
                status=status.HTTP_409_CONFLICT,
            )

        input_serializer = CompletenessCheckInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        if validated["approved"]:
            services.approve_completeness(article, request.user)
        else:
            services.return_for_revision(article, request.user, validated["comment"])

        return Response({"status": article.status})


class ArticleVersionsView(APIView):
    """POST /api/articles/{id}/versions — TS section 7 (US-3): files + author comment only, no metadata."""

    permission_classes = [HasRole(Role.AUTHOR)]

    def post(self, request, article_id):
        article = _get_owned_article_or_404(article_id, request.user)
        if article.status != Article.NEEDS_REVISION:
            return Response(
                {"code": "not_in_revision", "message": "Статья не находится на доработке."},
                status=status.HTTP_409_CONFLICT,
            )

        input_serializer = VersionUploadInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        try:
            validate_manuscript_file(validated["manuscriptFile"])
        except serializers.ValidationError as exc:
            return Response(
                {
                    "code": "invalid_manuscript",
                    "message": str(exc.detail[0]),
                    "fieldErrors": {"manuscriptFile": [str(exc.detail[0])]},
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        doc_files = request.FILES.getlist("documents")
        doc_types = _parse_document_types(request.data.get("documentTypes"))

        version = services.add_revision_version(
            article,
            validated["manuscriptFile"],
            doc_files,
            doc_types,
            validated["authorComment"],
        )

        return Response({"versionId": str(version.id), "status": article.status})


class ArticleTopicCheckView(APIView):
    """POST /api/articles/{id}/topic-check — TS section 7 (US-4)."""

    permission_classes = [HasRole(Role.CHIEF_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        if article.status != Article.SUBMITTED or article.completeness_approved_at is None or article.reviews.exists():
            return Response(
                {"code": "not_in_queue", "message": "Статья не находится в очереди проверки тематики."},
                status=status.HTTP_409_CONFLICT,
            )

        input_serializer = TopicCheckInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        if validated["approved"]:
            services.approve_topic(article, request.user)
        else:
            services.reject_topic(article, request.user, validated["comment"])

        return Response({"status": article.status})


class ArticleReviewersView(APIView):
    """POST /api/articles/{id}/reviewers — TS section 7 (US-4)."""

    permission_classes = [HasRole(Role.CHIEF_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        if article.status != Article.SUBMITTED or article.completeness_approved_at is None or article.reviews.exists():
            return Response(
                {"code": "not_in_queue", "message": "Статья не находится в очереди проверки тематики."},
                status=status.HTTP_409_CONFLICT,
            )

        input_serializer = ReviewerAssignmentInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        try:
            reviews = review_services.assign_reviewers(
                article, request.user, validated["reviewerIds"], validated["deadline"]
            )
        except ValueError as exc:
            return Response(
                {"code": "invalid_reviewers", "message": str(exc), "fieldErrors": {"reviewerIds": [str(exc)]}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response({"reviews": ReviewSerializer(reviews, many=True).data})


class ArticleDecisionView(APIView):
    """POST /api/articles/{id}/decision — TS section 7 (US-7)."""

    permission_classes = [HasRole(Role.CHIEF_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)

        input_serializer = DecisionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        try:
            services.make_review_decision(article, request.user, validated["decision"], validated["comment"])
        except ValueError as exc:
            return Response({"code": "not_ready", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"status": article.status})


class ArticleAssignDoiView(APIView):
    """POST /api/articles/{id}/doi — TS section 7 (US-9). Empty body."""

    permission_classes = [HasRole(Role.TECH_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        try:
            services.assign_doi(article, request.user)
        except ValueError as exc:
            return Response({"code": "not_ready", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"doi": article.doi})


class ArticlePublishView(APIView):
    """POST /api/articles/{id}/publish — TS section 7 (US-9)."""

    permission_classes = [HasRole(Role.TECH_EDITOR)]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)

        input_serializer = PublishInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        issue = get_object_or_404(Issue, pk=input_serializer.validated_data["issueId"])

        try:
            services.publish_article(article, request.user, issue)
        except ValueError as exc:
            return Response({"code": "not_ready", "message": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response({"status": article.status, "publishedAt": article.published_at})


class ArticleListView(APIView):
    """
    GET /api/articles — TS section 7. Own articles for authors; chief
    editors see all articles instead (M3c plan decision #6 — needed for
    their "Управление статьями" screen). Optional ?status= filter throughout.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.roles.filter(code=Role.CHIEF_EDITOR).exists():
            qs = Article.objects.all()
        else:
            qs = Article.objects.filter(submitted_by=request.user)

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response({"items": ArticleListSerializer(qs, many=True).data})


class ArticleDetailView(APIView):
    """GET /api/articles/{id} — TS section 7: {article, versions, reviews, decisions}."""

    permission_classes = [IsAuthenticated]

    def get(self, request, article_id):
        article = _get_visible_article_or_404(article_id, request.user)
        return Response(
            {
                "article": ArticleDetailSerializer(article).data,
                # context carries the request so FileField(use_url=True) builds
                # absolute URLs — without it, DRF falls back to MEDIA_URL's bare
                # relative path, which the frontend (a different origin/port)
                # resolves against itself instead of the API, breaking every
                # manuscript/document link (PDF viewer included).
                "versions": ArticleVersionSerializer(
                    article.versions.all(), many=True, context={"request": request}
                ).data,
                "reviews": ReviewSerializer(article.reviews.all(), many=True).data,
                "decisions": EditorialDecisionSerializer(article.decisions.all(), many=True).data,
            }
        )
