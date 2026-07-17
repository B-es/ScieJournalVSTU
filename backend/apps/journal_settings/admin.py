from django.contrib import admin

from .models import JournalSettings


@admin.register(JournalSettings)
class JournalSettingsAdmin(admin.ModelAdmin):
    list_display = ("journal_name_ru", "issn")

    def has_add_permission(self, request):
        # Singleton — only allow creating the record if it doesn't exist yet.
        return not JournalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
