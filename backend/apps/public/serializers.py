from rest_framework import serializers

from apps.articles.models import Article
from apps.articles.serializers import ArticleAuthorSerializer
from apps.issues.models import Issue


class PublicArticleListSerializer(serializers.ModelSerializer):
    """
    US-10: card shape for search results / archive / home — same field set as
    the detail serializer minus the manuscript/PDF link (that's only fetched
    once a reader opens the article itself).
    """

    titleRu = serializers.CharField(source="title_ru")
    titleEn = serializers.CharField(source="title_en")
    abstractRu = serializers.CharField(source="abstract_ru")
    abstractEn = serializers.CharField(source="abstract_en")
    keywordsRu = serializers.ListField(source="keywords_ru", child=serializers.CharField())
    keywordsEn = serializers.ListField(source="keywords_en", child=serializers.CharField())
    pagesCount = serializers.IntegerField(source="pages_count")
    publishedAt = serializers.DateTimeField(source="published_at")
    issueNumber = serializers.IntegerField(source="issue.number", default=None)
    issueYear = serializers.IntegerField(source="issue.year", default=None)
    authors = ArticleAuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "titleRu",
            "titleEn",
            "abstractRu",
            "abstractEn",
            "keywordsRu",
            "keywordsEn",
            "topic",
            "doi",
            "pagesCount",
            "publishedAt",
            "issueNumber",
            "issueYear",
            "authors",
        ]


class PublicArticleDetailSerializer(PublicArticleListSerializer):
    """
    US-10: article page — same public-safe fields as the list card. Internal
    fields (status, completenessApprovedAt, lastAutosavedAt) from the
    cabinet's ArticleDetailSerializer are deliberately not repeated here,
    since every article reachable through this serializer is always
    `published` by construction (the view filters on that before serializing).
    """


class PublicIssueListSerializer(serializers.ModelSerializer):
    """US-10: archive/home card — adds aggregate counts for the DS "Выпуск журнала" component."""

    descriptionRu = serializers.CharField(source="description_ru")
    descriptionEn = serializers.CharField(source="description_en")
    coverImageUrl = serializers.ImageField(source="cover_image", use_url=True)
    publishedAt = serializers.DateTimeField(source="published_at")
    articlesCount = serializers.SerializerMethodField()
    pagesCount = serializers.SerializerMethodField()
    authorsCount = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "number",
            "year",
            "title",
            "descriptionRu",
            "descriptionEn",
            "coverImageUrl",
            "publishedAt",
            "language",
            "articlesCount",
            "pagesCount",
            "authorsCount",
        ]

    def _published_articles(self, issue):
        # Small per-issue querysets — fine at MVP data volumes (see plan #decision 5).
        return issue.articles.filter(status=Article.PUBLISHED)

    def get_articlesCount(self, issue):
        return self._published_articles(issue).count()

    def get_pagesCount(self, issue):
        total = 0
        for pages in self._published_articles(issue).values_list("pages_count", flat=True):
            total += pages or 0
        return total

    def get_authorsCount(self, issue):
        return (
            self._published_articles(issue)
            .values_list("authors__id", flat=True)
            .distinct()
            .count()
        )
