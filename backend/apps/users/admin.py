from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Role, User, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Technical editor manages users/roles here (TS section 5 admin panel note)."""

    ordering = ("email",)
    list_display = ("email", "full_name", "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff", "roles")
    search_fields = ("email", "full_name")
    readonly_fields = ("id", "created_at", "last_login")
    inlines = [UserRoleInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Профиль", {"fields": ("full_name", "affiliation", "orcid", "language_pref")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2"),
        }),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code",)
