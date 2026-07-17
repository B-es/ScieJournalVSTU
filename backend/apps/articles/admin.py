from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.shortcuts import render

from apps.issues.models import Issue

from . import services
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


class ReturnForRevisionForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, label="Комментарий (обязательно)")
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class PublishArticleForm(forms.Form):
    issue = forms.ModelChoiceField(queryset=Issue.objects.all(), label="Выпуск")
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


def _eligible_for_completeness_check(queryset):
    """US-2 queue: submitted and not yet checked (see Article.completeness_approved_at, plan decision #3)."""
    return queryset.filter(status=Article.SUBMITTED, completeness_approved_at__isnull=True)


@admin.action(description="Подтвердить комплектность")
def approve_completeness_action(modeladmin, request, queryset):
    eligible = _eligible_for_completeness_check(queryset)
    count = eligible.count()
    skipped = queryset.count() - count

    for article in eligible:
        services.approve_completeness(article, request.user)

    if count:
        modeladmin.message_user(request, f"Комплектность подтверждена: {count}.", level=messages.SUCCESS)
    if skipped:
        modeladmin.message_user(
            request,
            f"Пропущено без изменений: {skipped} (нужен статус «На рассмотрении», ещё не проверенные).",
            level=messages.WARNING,
        )


@admin.action(description="Вернуть на доработку (с комментарием)")
def return_for_revision_action(modeladmin, request, queryset):
    """
    Standard Django admin "action with an intermediate page" pattern (same
    shape as the built-in delete_selected) — a comment is mandatory here per
    PRD section 7, so a plain one-click bulk action isn't enough.
    """
    eligible = _eligible_for_completeness_check(queryset)
    if not eligible.exists():
        modeladmin.message_user(
            request,
            "Нет подходящих статей: нужен статус «На рассмотрении», ещё не проверенные.",
            level=messages.WARNING,
        )
        return None

    if "apply" in request.POST:
        form = ReturnForRevisionForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            for article in eligible:
                services.return_for_revision(article, request.user, comment)
            modeladmin.message_user(request, f"Возвращено на доработку: {eligible.count()}.", level=messages.SUCCESS)
            return None
    else:
        form = ReturnForRevisionForm(
            initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)}
        )

    return render(
        request,
        "admin/articles/return_for_revision.html",
        context={"articles": eligible, "form": form, "title": "Вернуть статьи на доработку"},
    )


@admin.action(description="Присвоить DOI")
def assign_doi_action(modeladmin, request, queryset):
    """US-9: no intermediate page needed — assign_doi generates the DOI itself (M3f plan #2)."""
    eligible = queryset.filter(status=Article.ACCEPTED, doi="")
    count = 0
    for article in eligible:
        try:
            services.assign_doi(article, request.user)
            count += 1
        except ValueError as exc:
            modeladmin.message_user(request, f"{article}: {exc}", level=messages.WARNING)

    skipped = queryset.count() - count
    if count:
        modeladmin.message_user(request, f"DOI присвоен: {count}.", level=messages.SUCCESS)
    if skipped:
        modeladmin.message_user(
            request,
            f"Пропущено без изменений: {skipped} (нужен статус «Принята к публикации» без уже присвоенного DOI).",
            level=messages.WARNING,
        )


@admin.action(description="Опубликовать в выпуске")
def publish_article_action(modeladmin, request, queryset):
    """US-9: needs an Issue picked — same intermediate-page pattern as return_for_revision_action."""
    eligible = queryset.filter(status=Article.ACCEPTED).exclude(doi="")
    if not eligible.exists():
        modeladmin.message_user(
            request,
            "Нет подходящих статей: нужен статус «Принята к публикации» с уже присвоенным DOI.",
            level=messages.WARNING,
        )
        return None

    if "apply" in request.POST:
        form = PublishArticleForm(request.POST)
        if form.is_valid():
            issue = form.cleaned_data["issue"]
            for article in eligible:
                services.publish_article(article, request.user, issue)
            modeladmin.message_user(request, f"Опубликовано: {eligible.count()}.", level=messages.SUCCESS)
            return None
    else:
        form = PublishArticleForm(initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)})

    return render(
        request,
        "admin/articles/publish_article.html",
        context={"articles": eligible, "form": form, "title": "Опубликовать статьи в выпуске"},
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "status", "completeness_approved_at", "submitted_by", "topic", "doi", "created_at")
    list_filter = ("status", "completeness_approved_at", "topic")
    search_fields = ("title_ru", "title_en", "doi")
    inlines = [ArticleAuthorInline, ArticleVersionInline]
    readonly_fields = ("id", "created_at", "updated_at", "last_autosaved_at")
    actions = [approve_completeness_action, return_for_revision_action, assign_doi_action, publish_article_action]


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ("article", "version_number", "submitted_at")
    inlines = [ArticleDocumentInline]
