from __future__ import annotations

from datetime import date

import pytest

from apps.articles.models import Article
from apps.issues.models import Issue
from apps.journal_settings.models import JournalSettings
from apps.reviews.models import Review
from apps.users.models import Role, User


@pytest.fixture(autouse=True)
def temporary_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def role_factory(db):
    def create(code: str) -> Role:
        role, _ = Role.objects.get_or_create(code=code)
        return role

    return create


@pytest.fixture
def user_factory(db, role_factory):
    counter = 0

    def create(*, role: str | None = None, email: str | None = None, full_name: str | None = None) -> User:
        nonlocal counter
        counter += 1
        user = User.objects.create_user(
            email=email or f"user{counter}@example.com",
            password="StrongPass123",
            full_name=full_name or f"Пользователь {counter}",
        )
        if role:
            user.roles.add(role_factory(role))
        return user

    return create


@pytest.fixture
def author(user_factory):
    return user_factory(role=Role.AUTHOR, email="author@example.com", full_name="Автор")


@pytest.fixture
def editor(user_factory):
    return user_factory(role=Role.CHIEF_EDITOR, email="editor@example.com", full_name="Редактор")


@pytest.fixture
def tech_editor(user_factory):
    return user_factory(role=Role.TECH_EDITOR, email="tech@example.com", full_name="Техредактор")


@pytest.fixture
def reviewer_factory(user_factory):
    def create(*, email: str | None = None, full_name: str | None = None) -> User:
        return user_factory(role=Role.REVIEWER, email=email, full_name=full_name)

    return create


@pytest.fixture
def article_factory(db, author):
    counter = 0

    def create(**overrides) -> Article:
        nonlocal counter
        counter += 1
        values = {
            "title_ru": f"Тестовая статья {counter}",
            "title_en": f"Test article {counter}",
            "abstract_ru": "Аннотация",
            "abstract_en": "Abstract",
            "keywords_ru": ["наука", "тест"],
            "keywords_en": ["science", "test"],
            "topic": "Архитектура",
            "submitted_by": author,
            "status": Article.SUBMITTED,
        }
        values.update(overrides)
        return Article.objects.create(**values)

    return create


@pytest.fixture
def article(article_factory):
    return article_factory()


@pytest.fixture
def issue(db):
    return Issue.objects.create(number=1, year=2026, title="Выпуск 1")


@pytest.fixture
def review_factory(db, article, reviewer_factory):
    counter = 0

    def create(**overrides) -> Review:
        nonlocal counter
        counter += 1
        values = {
            "article": article,
            "reviewer": reviewer_factory(email=f"reviewer{counter}@example.com"),
            "deadline": date(2026, 12, 31),
            "invitation_status": Review.INVITED,
        }
        values.update(overrides)
        return Review.objects.create(**values)

    return create


@pytest.fixture
def journal_settings(db):
    settings = JournalSettings.load()
    settings.journal_name_ru = "Научный журнал ВолгГТУ"
    settings.journal_name_en = "VSTU Scientific Journal"
    settings.save()
    return settings
