from django.contrib import admin

from .models import EditorialDecision


@admin.register(EditorialDecision)
class EditorialDecisionAdmin(admin.ModelAdmin):
    list_display = ("article", "editor", "stage", "decision", "created_at")
    list_filter = ("stage", "decision")
