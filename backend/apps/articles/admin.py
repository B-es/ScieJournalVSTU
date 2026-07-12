from django.contrib import admin

from .models import Article, ArticleAuthor, ArticleDocument, ArticleVersion


class ArticleAuthorInline(admin.TabularInline):
    model = ArticleAuthor
    extra = 1


class ArticleDocumentInline(admin.TabularInline):
    model = ArticleDocument
    extra = 0


class ArticleVersionInline(admin.TabularInline):
    model = ArticleVersion
    extra = 0
    show_change_link = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "status", "submitted_by", "topic", "doi", "created_at")
    list_filter = ("status", "topic")
    search_fields = ("title_ru", "title_en", "doi")
    inlines = [ArticleAuthorInline, ArticleVersionInline]
    readonly_fields = ("id", "created_at", "updated_at", "last_autosaved_at")


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ("article", "version_number", "submitted_at")
    inlines = [ArticleDocumentInline]
