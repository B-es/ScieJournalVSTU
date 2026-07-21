<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import * as reviewsApi from "~/api/reviews";
import StatusBadge from "~/components/StatusBadge.vue";
import DecisionForm from "~/components/cabinet/DecisionForm.vue";
import ReviewersPanel from "~/components/cabinet/ReviewersPanel.vue";
import TopicCheckForm from "~/components/cabinet/TopicCheckForm.vue";
import ArticleReviewSummary from "~/components/cabinet/ArticleReviewSummary.vue";
import PdfViewer from "~/components/cabinet/PdfViewer.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<articlesApi.ArticleDetailResponse | null>(null);
const reviewers = ref<reviewsApi.ReviewItem[]>([]);
const loading = ref(true);
const error = ref("");

const inTopicCheckQueue = computed(() => {
    const article = detail.value?.article;
    if (!article) return false;
    return (
        article.status === "submitted" &&
        !!article.completenessApprovedAt &&
        (detail.value?.reviews?.length ?? 0) === 0
    );
});

const canMakeDecision = computed(() => {
    const reviews = detail.value?.reviews ?? [];
    const acceptedReviews = reviews.filter(r => r.invitationStatus === "accepted");
    const submittedReviews = acceptedReviews.filter(r => r.submittedAt);
    return (
        detail.value?.article.status === "in_review" &&
        acceptedReviews.length > 0 &&
        submittedReviews.length === acceptedReviews.length
    );
});

const latestVersion = computed(() => {
    const versions = detail.value?.versions ?? [];
    return versions.length > 0 ? versions[versions.length - 1] : null;
});

const manuscriptUrl = computed(() => {
    return latestVersion.value?.manuscriptFileUrl ?? "";
});

const reviewerMap = computed(() => {
    const map: Record<string, { fullName: string; email: string }> = {};
    reviewers.value.forEach(r => {
        map[r.reviewerId] = {
            fullName: r.reviewerFullName,
            email: r.reviewerEmail
        };
    });
    return map;
});

const enrichedReviews = computed(() => {
    return (detail.value?.reviews ?? []).map(review => ({
        ...review,
        reviewerName: reviewerMap.value[review.reviewerId]?.fullName || `ID: ${review.reviewerId.slice(0, 8)}`,
        reviewerEmail: reviewerMap.value[review.reviewerId]?.email || ''
    }));
});

const submittedReviews = computed(() => {
    return enrichedReviews.value.filter(r => r.submittedAt);
});

const hasReviewFiles = computed(() => {
    return submittedReviews.value.some((r) => r.reviewFileUrl);
});

const latestDecision = computed(() => {
    const decisions = detail.value?.decisions ?? [];
    return decisions.length > 0 ? decisions[decisions.length - 1] : null;
});

const reviewStatus = computed(() => {
    const reviews = detail.value?.reviews ?? [];
    const accepted = reviews.filter(r => r.invitationStatus === "accepted");
    const submitted = accepted.filter(r => r.submittedAt);
    const invited = reviews.filter(r => r.invitationStatus === "invited");
    const declined = reviews.filter(r => r.invitationStatus === "declined");
    
    return {
        total: reviews.length,
        accepted: accepted.length,
        submitted: submitted.length,
        invited: invited.length,
        declined: declined.length,
        isComplete: accepted.length > 0 && submitted.length === accepted.length
    };
});

async function load() {
    loading.value = true;
    error.value = "";
    try {
        detail.value = await articlesApi.getArticle(articleId);
        
        const reviewsRes = await reviewsApi.listMyReviews(undefined, articleId);
        reviewers.value = reviewsRes.items;
    } catch {
        error.value = t("articlePage.notFound");
    } finally {
        loading.value = false;
    }
}

onMounted(load);
</script>

<template>
    <div class="chief-editor-article-page">
        <p v-if="loading" class="article-page__state">{{ t("common.loading") }}</p>
        <p v-else-if="error" class="article-page__state article-page__state--error" role="alert">{{ error }}</p>

        <template v-else-if="detail">
            <header class="article-page__header">
                <div class="article-page__title-wrapper">
                    <h2 class="article-page__title">{{ detail.article.titleRu }}</h2>
                    <StatusBadge :status="(detail.article.status as any)" />
                </div>
                
                <div class="article-page__author-info">
                    <span class="article-page__author-name">
                        {{ detail.article.authors.find(a => a.order === 0)?.fullName || t("articlePage.unknownAuthor") }}
                    </span>
                </div>
            </header>

            <PdfViewer 
                v-if="manuscriptUrl" 
                :file-url="manuscriptUrl" 
                :confidential="true"
            />

            <TopicCheckForm
                v-if="inTopicCheckQueue"
                :article-id="articleId"
                @done="load"
            />

            <ReviewersPanel
                v-if="!inTopicCheckQueue && detail.reviews.length > 0"
                :article-id="articleId"
                @changed="load"
            />

            <DecisionForm
                v-if="detail.article.status === 'in_review'"
                :article-id="articleId"
                :reviews="detail.reviews"
                @decided="load"
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
                    <div v-if="detail.article.doi" class="article-page__metadata-item">
                        <dt>{{ t("articlePage.doiLabel") }}</dt>
                        <dd><code>{{ detail.article.doi }}</code></dd>
                    </div>
                    <div v-if="detail.article.pagesCount" class="article-page__metadata-item">
                        <dt>{{ t("articlePage.pagesCount") }}</dt>
                        <dd>{{ detail.article.pagesCount }}</dd>
                    </div>
                    <div v-if="detail.article.createdAt" class="article-page__metadata-item">
                        <dt>{{ t("articlePage.createdAt") }}</dt>
                        <dd>{{ new Date(detail.article.createdAt).toLocaleDateString('ru-RU') }}</dd>
                    </div>
                    <div v-if="detail.article.submittedAt" class="article-page__metadata-item">
                        <dt>{{ t("articlePage.submittedAt") }}</dt>
                        <dd>{{ new Date(detail.article.submittedAt).toLocaleDateString('ru-RU') }}</dd>
                    </div>
                </dl>
            </section>

            <section v-if="submittedReviews.length" class="article-page__section article-page__reviews">
                <h3 class="article-page__section-title">
                    {{ t("articlePage.reviews") }}
                </h3>
                
                <div class="article-page__reviews-list">
                    <ArticleReviewSummary 
                        v-for="review in submittedReviews" 
                        :key="review.id" 
                        :review="review"
                        :show-reviewer-name="true"
                    />
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
                            <span class="article-page__history-stage">
                                {{ t(`decisionForm.stage.${decision.stage}`) }}
                            </span>
                            <span class="article-page__history-editor">
                                {{ t("articlePage.editor") }}: {{ decision.editorId.slice(0, 8) }}
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

            <section v-if="detail.versions.length > 1" class="article-page__section article-page__versions">
                <h3 class="article-page__section-title">{{ t("articlePage.versions") }}</h3>
                
                <div class="article-page__versions-list">
                    <div 
                        v-for="version in detail.versions" 
                        :key="version.id"
                        class="article-page__version-item"
                    >
                        <div class="article-page__version-header">
                            <span class="article-page__version-number">
                                {{ t("articlePage.version") }} {{ version.versionNumber }}
                            </span>
                            <span class="article-page__version-date">
                                {{ new Date(version.submittedAt).toLocaleDateString('ru-RU') }}
                            </span>
                        </div>
                        <p v-if="version.authorComment" class="article-page__version-comment">
                            <strong>{{ t("articlePage.authorComment") }}:</strong>
                            {{ version.authorComment }}
                        </p>
                        <a 
                            v-if="version.manuscriptFileUrl"
                            :href="version.manuscriptFileUrl" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            class="article-page__version-download"
                        >
                            {{ t("articlePage.downloadManuscript") }}
                        </a>
                    </div>
                </div>
            </section>
        </template>
    </div>
</template>

<style scoped>
.chief-editor-article-page {
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

.article-page__author-info {
    margin-top: var(--spacing-sm);
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.article-page__author-label {
    font-weight: 500;
}

.article-page__author-name {
    color: var(--color-text-primary);
}

.article-page__review-status {
    padding: var(--spacing-md);
    background: var(--color-surface);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    margin-bottom: var(--spacing-lg);
}

.article-page__review-status-title {
    margin: 0 0 var(--spacing-sm);
    font-size: var(--type-body-size);
    font-weight: 600;
    color: var(--color-text-primary);
}

.article-page__review-status-stats {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
}

.stat-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.stat-label {
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.stat-value {
    font-weight: 600;
    font-size: var(--type-body-size);
}

.stat-value--accepted {
    color: var(--color-success);
}

.stat-value--submitted {
    color: var(--color-primary);
}

.stat-value--invited {
    color: var(--color-warning);
}

.stat-value--declined {
    color: var(--color-error);
}

.article-page__review-status-complete {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(46, 125, 50, 0.1);
    color: var(--color-success);
    border-radius: var(--radius-sm);
    font-weight: 500;
    font-size: var(--type-caption-size);
}

.article-page__review-status-waiting {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(237, 108, 2, 0.1);
    color: var(--color-warning);
    border-radius: var(--radius-sm);
    font-weight: 500;
    font-size: var(--type-caption-size);
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

.article-page__metadata-item dd code {
    background: var(--color-surface);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-size: var(--type-caption-size);
}

.article-page__reviews-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
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

.article-page__history-editor {
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

.article-page__versions-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.article-page__version-item {
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
    background: var(--color-surface);
}

.article-page__version-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
}

.article-page__version-number {
    font-weight: 600;
    color: var(--color-text-primary);
}

.article-page__version-date {
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.article-page__version-comment {
    margin: var(--spacing-xs) 0;
    font-size: var(--type-body-size);
    color: var(--color-text-primary);
}

.article-page__version-download {
    display: inline-block;
    font-size: var(--type-caption-size);
    color: var(--color-primary);
    text-decoration: none;
}

.article-page__version-download:hover {
    text-decoration: underline;
}
</style>