<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import ArticleRevisionForm from "~/components/cabinet/ArticleRevisionForm.vue";
import ArticleSubmitForm from "~/components/cabinet/ArticleSubmitForm.vue";
import ArticleReviewSummary from "~/components/cabinet/ArticleReviewSummary.vue";
import StatusBadge from "~/components/StatusBadge.vue";
import PdfViewer from "~/components/cabinet/PdfViewer.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<articlesApi.ArticleDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

function latestDecision(decision: "revise" | "reject" | "accept") {
    const decisions = detail.value?.decisions ?? [];
    const matches = decisions
        .filter((d) => d.decision === decision)
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    return matches[0];
}

// Any stage can send an article to revision now (completeness check, M3b —
// the technical editor; review decision, M3e — the chief editor) — track
// which stage it came from so the right role gets credited in the label.
const latestRevision = computed(() => latestDecision("revise"));
const latestRevisionComment = computed(() => latestRevision.value?.comment ?? "");
const latestRevisionStage = computed(() => latestRevision.value?.stage ?? "");

const revisionCommentLabel = computed(() => {
    if (latestRevisionStage.value === "completeness_check") {
        return t("articlePage.techEditorComment");
    } else if (latestRevisionStage.value === "review_decision") {
        return t("articlePage.editorComment");
    }
    return t("articlePage.editorComment");
});

const latestRejection = computed(() => latestDecision("reject"));
const latestRejectionComment = computed(() => latestRejection.value?.comment ?? "");

const latestAcceptance = computed(() => latestDecision("accept"));
const latestAcceptanceComment = computed(() => latestAcceptance.value?.comment ?? "");

const reviewerComments = computed(() => {
    return (detail.value?.reviews ?? [])
        .filter((r) => r.submittedAt && r.commentsForAuthor)
        .map((r) => r.commentsForAuthor)
        .filter(Boolean);
});

const submittedReviews = computed(() => {
    return (detail.value?.reviews ?? []).filter((r) => r.submittedAt);
});

const hasReviewFiles = computed(() => {
    return submittedReviews.value.some((r) => r.reviewFileUrl);
});

const latestVersion = computed(() => {
    const versions = detail.value?.versions ?? [];
    return versions.length > 0 ? versions[versions.length - 1] : null;
});

const manuscriptUrl = computed(() => {
    return latestVersion.value?.manuscriptFileUrl ?? "";
});

async function load() {
    loading.value = true;
    error.value = "";
    try {
        detail.value = await articlesApi.getArticle(articleId);
    } catch {
        error.value = t("articlePage.notFound");
    } finally {
        loading.value = false;
    }
}

onMounted(load);
</script>

<template>
    <div class="article-page">
        <p v-if="loading">{{ t("common.loading") }}</p>
        <p v-else-if="error" role="alert">{{ error }}</p>

        <template v-else-if="detail">
            <header class="article-page__header">
              <h2>{{ detail.article.titleRu }}</h2>
              <StatusBadge :status="(detail.article.status as any)" />
            </header>

            <section v-if="detail.article.status === 'draft'" class="article-page__section">
                <ArticleSubmitForm :article-id="articleId" @submitted="load" />
            </section>

            <template v-else>
                <div class="article-page__notifications">
                    <template v-if="detail.article.status === 'needs_revision'">
                        <div class="article-page__notification article-page__notification--revision">
                            <p v-if="latestRevisionComment" class="article-page__notification-message">
                                <strong>{{ revisionCommentLabel }}:</strong>
                                {{ latestRevisionComment }}
                            </p>
                            <p v-if="reviewerComments.length" class="article-page__notification-message">
                                <strong>{{ t("articlePage.reviewerFeedback") }}:</strong>
                            </p>
                            <ul v-if="reviewerComments.length" class="article-page__reviewer-comments">
                                <li v-for="(comment, idx) in reviewerComments" :key="idx">
                                    {{ comment }}
                                </li>
                            </ul>
                        </div>
                    </template>

                    <template v-else-if="detail.article.status === 'rejected'">
                        <div class="article-page__notification article-page__notification--rejected">
                            <p v-if="latestRejectionComment" class="article-page__notification-message">
                                <strong>{{ t("articlePage.editorComment") }}:</strong>
                                {{ latestRejectionComment }}
                            </p>
                        </div>
                    </template>

                    <template v-else-if="detail.article.status === 'accepted'">
                        <div class="article-page__notification article-page__notification--accepted">
                            <p v-if="latestAcceptanceComment" class="article-page__notification-message">
                                <strong>{{ t("articlePage.editorComment") }}:</strong>
                                {{ latestAcceptanceComment }}
                            </p>
                            <p v-if="detail.article.doi" class="article-page__notification-message">
                                <strong>{{ t("articlePage.doiLabel") }}:</strong>
                                {{ detail.article.doi }}
                            </p>
                        </div>
                    </template>

                    <template v-else-if="detail.article.status === 'published'">
                        <div class="article-page__notification article-page__notification--published">
                            <div class="article-page__notification-meta">
                                <p v-if="detail.article.doi" class="article-page__notification-message">
                                    <strong>{{ t("articlePage.doiLabel") }}:</strong>
                                    {{ detail.article.doi }}
                                </p>
                                <p v-if="detail.article.issueNumber" class="article-page__notification-message">
                                    <strong>{{ t("articlePage.issueLabel") }}:</strong>
                                    {{ t("issuePage.numberLabel", { n: detail.article.issueNumber }) }}
                                    ({{ detail.article.issueYear }})
                                </p>
                                <p v-if="detail.article.publishedAt" class="article-page__notification-message">
                                    <strong>{{ t("articlePage.publishedAt") }}:</strong>
                                    {{ new Date(detail.article.publishedAt).toLocaleDateString('ru-RU') }}
                                </p>
                            </div>
                        </div>
                    </template>

                    <template v-else-if="detail.article.status === 'submitted' || detail.article.status === 'in_review'">
                        <div class="article-page__notification article-page__notification--info">
                            <p class="article-page__notification-message">
                                {{ t("articlePage.readonlyNotice") }}
                            </p>
                        </div>
                    </template>
                </div>

                <PdfViewer 
                    v-if="manuscriptUrl" 
                    :file-url="manuscriptUrl" 
                    :confidential="true"
                />

                <ArticleRevisionForm
                    v-if="detail.article.status === 'needs_revision'"
                    :article-id="articleId"
                    @uploaded="load"
                />

                <section class="article-page__section article-page__metadata">
                    <h3 class="article-page__section-title">{{ t("articlePage.metadata") }}</h3>
                    
                    <dl class="article-page__metadata-list">
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.titleRu") }}</dt>
                            <dd>{{ detail.article.titleRu }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.titleEn") }}</dt>
                            <dd>{{ detail.article.titleEn }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.abstractRu") }}</dt>
                            <dd>{{ detail.article.abstractRu }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.abstractEn") }}</dt>
                            <dd>{{ detail.article.abstractEn }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.topic") }}</dt>
                            <dd>{{ detail.article.topic }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.keywordsRu") }}</dt>
                            <dd>{{ detail.article.keywordsRu.join(", ") }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.keywordsEn") }}</dt>
                            <dd>{{ detail.article.keywordsEn.join(", ") }}</dd>
                        </div>
                        <div class="article-page__metadata-item">
                            <dt>{{ t("articleForm.authorsTitle") }}</dt>
                            <dd>
                                {{ detail.article.authors.map((a) => a.fullName).join(", ") }}
                            </dd>
                        </div>
                        <div v-if="detail.article.pagesCount" class="article-page__metadata-item">
                            <dt>{{ t("articlePage.pagesCount") }}</dt>
                            <dd>{{ detail.article.pagesCount }}</dd>
                        </div>
                    </dl>
                </section>

                <section v-if="submittedReviews.length" class="article-page__section article-page__reviews">
                    <h3 class="article-page__section-title">
                        {{ t("Рецензии") }}
                    </h3>
                                        
                    <div class="article-page__reviews-list">
                        <ArticleReviewSummary 
                            v-for="review in submittedReviews" 
                            :key="review.id" 
                            :review="review"
                            :show-reviewer-name="false"
                        />
                    </div>
                </section>

                <section v-else-if="detail.article.status === 'in_review'" class="article-page__section article-page__reviews">
                    <h3 class="article-page__section-title">{{ t("articlePage.reviews") }}</h3>
                    <div class="article-page__reviews-waiting">
                        <p>{{ t("articlePage.reviewsWaiting") }}</p>
                        <p class="article-page__reviews-waiting-hint">
                            {{ t("articlePage.reviewsWaitingHint") }}
                        </p>
                    </div>
                </section>

                <section v-if="detail.decisions.length" class="article-page__section article-page__history">
                    <h3 class="article-page__section-title">{{ t("articlePage.statusHistory") }}</h3>
                    
                    <div class="article-page__history-list">
                        <div 
                            v-for="decision in detail.decisions" 
                            :key="decision.id"
                            class="article-page__history-item"
                            :class="`article-page__history-item--${decision.decision}`"
                        >
                            <div class="article-page__history-header">
                                <span class="article-page__history-decision">
                                    {{ t(`decisionForm.recommendation.${decision.decision}`) }}
                                </span>
                                <span class="article-page__history-date">
                                    {{ new Date(decision.createdAt).toLocaleDateString('ru-RU', {
                                        day: '2-digit',
                                        month: 'long',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    }) }}
                                </span>
                            </div>
                            <p v-if="decision.comment" class="article-page__history-comment">
                                {{ decision.comment }}
                            </p>
                        </div>
                    </div>
                </section>
            </template>
        </template>
    </div>
</template>

<style scoped>
.article-page {
    max-width: 100%;
}

.article-page__state {
    padding: var(--spacing-xl) 0;
    text-align: center;
    color: var(--color-text-secondary);
}

.article-page__state--error {
    color: var(--color-error);
}

.article-page__header {
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
}

.article-page__title-wrapper {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    flex-wrap: wrap;
}

.article-page__title {
    margin: 0;
    font-size: var(--type-h2-size);
    line-height: var(--type-h2-line);
    color: var(--color-text-primary);
}

.article-page__subtitle {
    margin: var(--spacing-xs) 0 0;
    font-size: var(--type-body-size);
    color: var(--color-text-secondary);
}

.article-page__section {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
}

.article-page__section-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin: 0 0 var(--spacing-md);
    font-size: var(--type-h3-size);
    line-height: var(--type-h3-line);
    color: var(--color-text-primary);
}

.article-page__section-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 var(--spacing-xs);
    border-radius: 12px;
    background: var(--color-primary);
    color: var(--color-text-inverse);
    font-size: var(--type-caption-size);
    font-weight: 600;
}

.article-page__notifications {
    margin-bottom: var(--spacing-lg);
}

.article-page__notification {
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    border-left: 4px solid transparent;
}

.article-page__notification--revision {
    background: rgba(237, 108, 2, 0.08);
    border-left-color: var(--color-warning);
}

.article-page__notification--rejected {
    background: rgba(210, 25, 25, 0.08);
    border-left-color: var(--color-error);
}

.article-page__notification--accepted {
    background: rgba(46, 125, 50, 0.08);
    border-left-color: var(--color-success);
}

.article-page__notification--published {
    background: rgba(25, 118, 210, 0.08);
    border-left-color: var(--color-primary);
}

.article-page__notification--info {
    background: var(--color-surface);
    border-left-color: var(--color-text-secondary);
}

.article-page__notification-title {
    margin: 0 0 var(--spacing-xs);
    font-size: var(--type-body-size);
    font-weight: 600;
    color: var(--color-text-primary);
}

.article-page__notification-message {
    margin: var(--spacing-xs) 0 0;
    font-size: var(--type-body-size);
    color: var(--color-text-primary);
    white-space: pre-wrap;
}

.article-page__notification-meta {
    margin-top: var(--spacing-sm);
    padding-top: var(--spacing-sm);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.article-page__reviewer-comments {
    margin: var(--spacing-sm) 0 0;
    padding-left: var(--spacing-lg);
    list-style-type: disc;
}

.article-page__reviewer-comments li {
    margin-bottom: var(--spacing-xs);
    color: var(--color-text-primary);
}

.article-page__metadata-list {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: var(--spacing-sm) var(--spacing-md);
    margin: 0;
}

.article-page__metadata-item {
    display: contents;
}

.article-page__metadata-item dt {
    padding: var(--spacing-xs) 0;
    font-size: var(--type-caption-size);
    font-weight: 500;
    color: var(--color-text-secondary);
}

.article-page__metadata-item dd {
    margin: 0;
    padding: var(--spacing-xs) 0;
    font-size: var(--type-body-size);
    color: var(--color-text-primary);
    word-break: break-word;
}

.article-page__reviews-hint {
    margin: 0 0 var(--spacing-md);
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.article-page__reviews-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.article-page__reviews-waiting {
    padding: var(--spacing-lg);
    text-align: center;
    background: var(--color-surface);
    border-radius: var(--radius-md);
    border: 1px dashed var(--color-border);
}

.article-page__reviews-waiting p {
    margin: 0;
    color: var(--color-text-secondary);
}

.article-page__reviews-waiting-hint {
    margin-top: var(--spacing-xs) !important;
    font-size: var(--type-caption-size);
}

.article-page__history-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.article-page__history-item {
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--color-border);
    background: var(--color-surface);
}

.article-page__history-item--accept {
    border-left-color: var(--color-success);
}

.article-page__history-item--reject {
    border-left-color: var(--color-error);
}

.article-page__history-item--revise {
    border-left-color: var(--color-warning);
}

.article-page__history-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--spacing-sm);
}

.article-page__history-decision {
    font-weight: 600;
    color: var(--color-text-primary);
}

.article-page__history-stage {
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.article-page__history-date {
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
    margin-left: auto;
}

.article-page__history-comment {
    margin: var(--spacing-xs) 0 0;
    font-size: var(--type-body-size);
    color: var(--color-text-primary);
    white-space: pre-wrap;
}
</style>