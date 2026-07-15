<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import StatusBadge from "~/components/StatusBadge.vue";
import DecisionForm from "~/components/cabinet/DecisionForm.vue";
import ReviewersPanel from "~/components/cabinet/ReviewersPanel.vue";
import TopicCheckForm from "~/components/cabinet/TopicCheckForm.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<articlesApi.ArticleDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

// Awaiting topic check: past completeness check, no reviewers assigned yet
// (M3c plan decision #2 — "submitted" alone can't distinguish this from
// "awaiting completeness check", hence completenessApprovedAt).
const inTopicCheckQueue = computed(() => {
  const article = detail.value?.article;
  if (!article) return false;
  return article.status === "submitted" && !!article.completenessApprovedAt && (detail.value?.reviews.length ?? 0) === 0;
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
  <div>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error" role="alert">{{ error }}</p>

    <template v-else-if="detail">
      <header class="article-page__header">
        <h2>{{ detail.article.titleRu }}</h2>
        <StatusBadge :status="(detail.article.status as any)" />
      </header>

      <dl class="article-page__summary">
        <dt>{{ t("articleForm.titleEn") }}</dt>
        <dd>{{ detail.article.titleEn }}</dd>
        <dt>{{ t("articleForm.abstractRu") }}</dt>
        <dd>{{ detail.article.abstractRu }}</dd>
        <dt>{{ t("articleForm.topic") }}</dt>
        <dd>{{ detail.article.topic }}</dd>
        <dt>{{ t("articleForm.authorsTitle") }}</dt>
        <dd>{{ detail.article.authors.map((a) => a.fullName).join(", ") }}</dd>
      </dl>

      <TopicCheckForm v-if="inTopicCheckQueue" :article-id="articleId" @done="load" />
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
    </template>
  </div>
</template>

<style scoped>
.article-page__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.article-page__summary {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.article-page__summary dt {
  color: var(--color-text-secondary);
}

.article-page__summary dd {
  margin: 0;
}
</style>
