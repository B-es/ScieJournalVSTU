from __future__ import annotations

import pytest
from django.utils import timezone

from apps.articles.models import ArticleAuthor
from apps.journal_settings.models import JournalSettings
from apps.public import services


pytestmark = pytest.mark.django_db


@pytest.fixture
def published_article(article, issue, journal_settings):
    article.status = article.PUBLISHED
    article.issue = issue
    article.doi = "10.36622/vstu.2026.abcdef12"
    article.pages_count = 12
    article.published_at = timezone.now()
    article.save(
        update_fields=[
            "status",
            "issue",
            "doi",
            "pages_count",
            "published_at",
        ]
    )
    ArticleAuthor.objects.create(
        article=article,
        full_name="Иванов И. И.",
        order=1,
    )
    ArticleAuthor.objects.create(
        article=article,
        full_name="Петров П. П.",
        order=2,
    )
    return article


def test_build_citation_rejects_unknown_format(published_article):
    with pytest.raises(ValueError, match="Неизвестный формат"):
        services.build_citation(published_article, "mla")


def test_build_citation_requires_doi(published_article):
    published_article.doi = ""

    with pytest.raises(ValueError, match="только для статей"):
        services.build_citation(published_article, services.GOST)


def test_gost_citation_contains_article_and_issue_data(published_article):
    citation = services.build_citation(published_article, services.GOST)

    assert "Иванов И. И., Петров П. П." in citation
    assert published_article.title_ru in citation
    assert "Научный журнал ВолгГТУ" in citation
    assert f"№ {published_article.issue.number}" in citation
    assert "С. 12" in citation
    assert f"DOI: {published_article.doi}" in citation


def test_apa_citation_contains_english_fields_and_doi(published_article):
    citation = services.build_citation(published_article, services.APA)

    assert published_article.title_en in citation
    assert "VSTU Scientific Journal" in citation
    assert "pp. 12" in citation
    assert f"https://doi.org/{published_article.doi}" in citation


def test_bibtex_citation_has_expected_fields(published_article):
    citation = services.build_citation(published_article, services.BIBTEX)

    assert citation.startswith("@article{vstu")
    assert "author = {Иванов И. И. and Петров П. П.}" in citation
    assert f"title = {{{published_article.title_en}}}" in citation
    assert f"doi = {{{published_article.doi}}}" in citation


def test_citation_without_pages_omits_pages_fragment(published_article):
    published_article.pages_count = None

    citation = services.build_citation(published_article, services.APA)

    assert "pp." not in citation


def test_journal_settings_load_is_singleton():
    first = JournalSettings.load()
    first.journal_name_ru = "Изменённое название"
    first.save()
    second = JournalSettings.load()

    assert first.id == second.id
    assert second.journal_name_ru == "Изменённое название"
    assert JournalSettings.objects.count() == 1


def test_journal_settings_forces_singleton_id():
    original = JournalSettings.load()
    singleton_id = original.id
    original.delete()
    another = JournalSettings(
        journal_name_ru="Другое",
        journal_name_en="Another",
        about_ru="",
        about_en="",
    )
    another.save()

    assert another.id == singleton_id
    assert JournalSettings.objects.count() == 1
    assert JournalSettings.load().journal_name_ru == "Другое"
