import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """DS section 6, entity User. Login is by email (TS section 8)."""

    LANGUAGE_CHOICES = [
        ("ru", "Русский"),
        ("en", "English"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, blank=True)
    orcid = models.CharField(max_length=32, blank=True)
    language_pref = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="ru")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    roles = models.ManyToManyField("Role", through="UserRole", related_name="users")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def has_role(self, code: str) -> bool:
        return self.roles.filter(code=code).exists()


class Role(models.Model):
    """DS section 6, entity Role. Matches PRD section 2 roles."""

    AUTHOR = "author"
    REVIEWER = "reviewer"
    CHIEF_EDITOR = "chief_editor"
    TECH_EDITOR = "tech_editor"

    CODE_CHOICES = [
        (AUTHOR, "Автор"),
        (REVIEWER, "Рецензент"),
        (CHIEF_EDITOR, "Главный редактор"),
        (TECH_EDITOR, "Технический редактор"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, choices=CODE_CHOICES, unique=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.get_code_display()


class UserRole(models.Model):
    """Through model for User N—N Role (DS section 6)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_roles"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} — {self.role}"
