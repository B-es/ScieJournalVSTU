from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from apps.articles.serializers import (
    CompletenessCheckInputSerializer,
    DecisionInputSerializer,
    JSONStringField,
    ReviewerAssignmentInputSerializer,
    TopicCheckInputSerializer,
)
from apps.articles.validators import MAX_MANUSCRIPT_SIZE_BYTES, validate_manuscript_file
from apps.editorial.models import EditorialDecision
from apps.issues.models import Issue
from apps.issues.serializers import IssueCreateInputSerializer
from apps.reviews.serializers import ReviewSubmitInputSerializer
from apps.users.models import Role, User
from apps.users.permissions import HasRole
from apps.users.serializers import RegisterSerializer


pytestmark = pytest.mark.django_db


def test_user_manager_requires_email():
    with pytest.raises(ValueError, match="Email is required"):
        User.objects.create_user(email="", password="password", full_name="Без email")


def test_user_manager_normalizes_domain_and_hashes_password():
    user = User.objects.create_user(
        email="Fred@EXAMPLE.COM",
        password="StrongPass123",
        full_name="Фред",
    )

    assert user.email == "Fred@example.com"
    assert user.check_password("StrongPass123")
    assert not user.is_staff
    assert not user.is_superuser


def test_superuser_flags_are_validated():
    with pytest.raises(ValueError, match="is_staff=True"):
        User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123",
            is_staff=False,
        )


def test_register_serializer_lowercases_email_and_hashes_password():
    serializer = RegisterSerializer(
        data={
            "fullName": "Новый автор",
            "email": "NEW@EXAMPLE.COM",
            "password": "StrongPass123",
        }
    )

    assert serializer.is_valid(), serializer.errors
    user = serializer.save()

    assert user.email == "new@example.com"
    assert user.full_name == "Новый автор"
    assert user.check_password("StrongPass123")


def test_register_serializer_rejects_duplicate_email(user_factory):
    user_factory(email="duplicate@example.com")
    serializer = RegisterSerializer(
        data={
            "fullName": "Дубликат",
            "email": "DUPLICATE@example.com",
            "password": "StrongPass123",
        }
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_has_role_permission_checks_authentication_and_role(user_factory):
    permission = HasRole(Role.CHIEF_EDITOR)

    anonymous_request = SimpleNamespace(user=AnonymousUser())
    assert not permission.has_permission(anonymous_request, None)

    author = user_factory(role=Role.AUTHOR)
    author_request = SimpleNamespace(user=author)
    assert not permission.has_permission(author_request, None)

    editor = user_factory(role=Role.CHIEF_EDITOR)
    editor_request = SimpleNamespace(user=editor)
    assert permission.has_permission(editor_request, None)


def test_json_string_field_accepts_native_and_encoded_json():
    field = JSONStringField()

    assert field.run_validation(["one", "two"]) == ["one", "two"]
    assert field.run_validation('{"answer": 42}') == {"answer": 42}


def test_json_string_field_rejects_invalid_json():
    with pytest.raises(ValidationError, match="Некорректный JSON"):
        JSONStringField().run_validation("{broken")


@pytest.mark.parametrize("filename", ["article.doc", "article.DOCX", "article.pdf"])
def test_manuscript_validator_accepts_supported_extensions(filename):
    validate_manuscript_file(SimpleUploadedFile(filename, b"content"))


def test_manuscript_validator_rejects_extension():
    with pytest.raises(ValidationError, match="Недопустимый формат"):
        validate_manuscript_file(SimpleUploadedFile("virus.exe", b"content"))


def test_manuscript_validator_rejects_oversized_file():
    file = SimpleNamespace(name="article.pdf", size=MAX_MANUSCRIPT_SIZE_BYTES + 1)

    with pytest.raises(ValidationError, match="Файл слишком большой"):
        validate_manuscript_file(file)


@pytest.mark.parametrize(
    ("serializer_class", "payload"),
    [
        (CompletenessCheckInputSerializer, {"approved": False, "comment": "   "}),
        (TopicCheckInputSerializer, {"approved": False, "comment": ""}),
    ],
)
def test_negative_editorial_checks_require_comment(serializer_class, payload):
    serializer = serializer_class(data=payload)

    assert not serializer.is_valid()
    assert "comment" in serializer.errors


def test_positive_editorial_check_does_not_require_comment():
    serializer = CompletenessCheckInputSerializer(data={"approved": True})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["comment"] == ""


def test_reviewer_assignment_requires_at_least_two_reviewers():
    serializer = ReviewerAssignmentInputSerializer(
        data={"reviewerIds": [str(uuid4())], "deadline": "2026-12-31"}
    )

    assert not serializer.is_valid()
    assert "reviewerIds" in serializer.errors


def test_final_decision_rejects_blank_comment():
    serializer = DecisionInputSerializer(
        data={"decision": EditorialDecision.ACCEPT, "comment": "  "}
    )

    assert not serializer.is_valid()
    assert "comment" in serializer.errors


def test_review_form_requires_comments_for_author():
    serializer = ReviewSubmitInputSerializer(
        data={
            "recommendation": "accept",
            "formData": {"commentsForEditor": "Скрытый комментарий"},
        }
    )

    assert not serializer.is_valid()
    assert "formData" in serializer.errors


def test_issue_serializer_rejects_duplicate_number_and_year(issue):
    serializer = IssueCreateInputSerializer(data={"number": issue.number, "year": issue.year})

    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors


def test_issue_serializer_accepts_new_issue():
    serializer = IssueCreateInputSerializer(
        data={"number": 2, "year": 2026, "descriptionRu": ""}
    )

    assert serializer.is_valid(), serializer.errors
    assert not Issue.objects.filter(number=2, year=2026).exists()
