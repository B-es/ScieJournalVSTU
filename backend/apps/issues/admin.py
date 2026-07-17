from django.contrib import admin

from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("number", "year", "title", "language", "published_at")
    list_filter = ("year", "language")
    ordering = ("-year", "-number")
