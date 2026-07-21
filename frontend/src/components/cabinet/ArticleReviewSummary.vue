<!-- frontend/src/components/cabinet/ArticleReviewSummary.vue -->

<script setup lang="ts">
import { FileText, Download, CheckCircle, XCircle, RotateCcw, Clock } from "lucide-vue-next";
import type { ArticleReviewSummary } from "~/api/articles";

const props = defineProps<{
    review: ArticleReviewSummary;
    showReviewerName?: boolean;
}>();

const { t } = useI18n();

const isSubmitted = computed(() => !!props.review.submittedAt);

const recommendationLabel = computed(() => {
    if (!props.review.recommendation) return '';
    return t(`reviewForm.recommendation.${props.review.recommendation}`);
});

const recommendationColor = computed(() => {
    switch (props.review.recommendation) {
        case 'accept': return 'var(--color-success)';
        case 'reject': return 'var(--color-error)';
        case 'revise': return 'var(--color-warning)';
        default: return 'var(--color-text-secondary)';
    }
});

const recommendationIcon = computed(() => {
    switch (props.review.recommendation) {
        case 'accept': return CheckCircle;
        case 'reject': return XCircle;
        case 'revise': return RotateCcw;
        default: return Clock;
    }
});

const formattedDate = computed(() => {
    if (!props.review.submittedAt) return '';
    return new Date(props.review.submittedAt).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
});

const hasReviewFile = computed(() => !!props.review.reviewFileUrl);
const hasComments = computed(() => !!props.review.commentsForAuthor);
</script>

<template>
    <div class="review-summary" :class="{ 'review-summary--submitted': isSubmitted }">
        <div v-if="isSubmitted" class="review-summary__body">
            <div v-if="review.recommendation" class="review-summary__recommendation">
                <component :is="recommendationIcon" :size="16" :style="{ color: recommendationColor }" />
                <span class="review-summary__recommendation-label">
                    {{ t('reviewForm.recommendationLabel') }}:
                </span>
                <span class="review-summary__recommendation-value" :style="{ color: recommendationColor }">
                    {{ recommendationLabel }}
                </span>
            </div>

            <div v-if="hasComments" class="review-summary__comments">
                <strong>{{ t('reviewForm.commentsForAuthor') }}:</strong>
                <p class="review-summary__comments-text">{{ review.commentsForAuthor }}</p>
            </div>

            <div v-if="hasReviewFile" class="review-summary__file">
                <FileText :size="16" class="review-summary__file-icon" />
                <a 
                    :href="review.reviewFileUrl" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="review-summary__file-link"
                >
                    {{ review.reviewFileName || t('reviewForm.downloadReviewFile') }}
                </a>
                <Download :size="14" class="review-summary__file-download-icon" />
            </div>

            <div class="review-summary__meta">
                <span class="review-summary__meta-value">{{ formattedDate }}</span>
            </div>
        </div>
    </div>
</template>

<style scoped>
.review-summary {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    background: var(--color-background);
    transition: all 0.2s ease;
}

.review-summary:hover {
    box-shadow: var(--shadow-sm);
}

.review-summary--submitted {
    border-left: 3px solid var(--color-success);
}

.review-summary__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
    flex-wrap: wrap;
    gap: var(--spacing-xs);
}

.review-summary__reviewer-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.review-summary__reviewer-label {
    font-weight: 500;
}

.review-summary__reviewer-name {
    color: var(--color-text-primary);
    font-weight: 500;
}

.review-summary__reviewer-anonymous {
    color: var(--color-text-secondary);
    font-style: italic;
}

.review-summary__status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--type-caption-size);
    font-weight: 500;
    white-space: nowrap;
}

.review-summary__status-badge--submitted {
    background: rgba(46, 125, 50, 0.1);
    color: var(--color-success);
}

.review-summary__status-badge--pending {
    background: var(--color-surface);
    color: var(--color-text-secondary);
}

.review-summary__body {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.review-summary__recommendation {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
}

.review-summary__recommendation-label {
    font-weight: 500;
    color: var(--color-text-secondary);
}

.review-summary__recommendation-value {
    font-weight: 600;
}

.review-summary__comments {
    padding: var(--spacing-sm);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
}

.review-summary__comments-text {
    margin: var(--spacing-xs) 0 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: var(--color-text-primary);
}

.review-summary__file {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
    transition: all 0.2s ease;
}

.review-summary__file:hover {
    background: var(--color-background);
    border-color: var(--color-primary);
}

.review-summary__file-icon {
    flex-shrink: 0;
    color: var(--color-primary);
}

.review-summary__file-link {
    flex: 1;
    color: var(--color-primary);
    text-decoration: none;
    font-size: var(--type-body-size);
    word-break: break-all;
}

.review-summary__file-link:hover {
    text-decoration: underline;
}

.review-summary__file-download-icon {
    flex-shrink: 0;
    color: var(--color-text-secondary);
    transition: color 0.2s ease;
}

.review-summary__file:hover .review-summary__file-download-icon {
    color: var(--color-primary);
}

.review-summary__meta {
    display: flex;
    gap: var(--spacing-xs);
    font-size: var(--type-caption-size);
    color: var(--color-text-secondary);
}

.review-summary__meta-label {
    font-weight: 500;
}

.review-summary__meta-value {
    color: var(--color-text-primary);
}
</style>