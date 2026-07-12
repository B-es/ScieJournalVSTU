from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("article", "reviewer", "invitation_status", "recommendation", "deadline", "submitted_at")
    list_filter = ("invitation_status", "recommendation")
    search_fields = ("article__title_ru", "reviewer__email")
