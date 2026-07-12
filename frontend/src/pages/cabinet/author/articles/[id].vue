<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import ArticleRevisionForm from "~/components/cabinet/ArticleRevisionForm.vue";
import ArticleSubmitForm from "~/components/cabinet/ArticleSubmitForm.vue";
import StatusBadge from "~/components/StatusBadge.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<articlesApi.ArticleDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

const latestRevisionComment = computed(() => {
  const decisions = detail.value?.decisions ?? [];
  const returns = decisions
    .filter((d) => d.stage === "completeness_check" && d.decision === "revise")
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  return returns[0]?.comment ?? "";
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

      <section v-if="detail.article.status === 'draft'">
        <ArticleSubmitForm :article-id="articleId" @submitted="load" />
      </section>

      <section v-else>
        <p v-if="detail.article.status === 'needs_revision' && latestRevisionComment" class="article-page__notice">
          <strong>{{ t("articlePage.techEditorComment") }}:</strong> {{ latestRevisionComment }}
        </p>
        <p v-else class="article-page__notice">{{ t("articlePage.readonlyNotice") }}</p>

        <h3>{{ t("articlePage.statusHistory") }}</h3>
        <p><StatusBadge :status="(detail.article.status as any)" /></p>

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

        <ArticleRevisionForm
          v-if="detail.article.status === 'needs_revision'"
          :article-id="articleId"
          @uploaded="load"
        />
      </section>
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

.article-page__notice {
  color: var(--color-text-secondary);
}

.article-page__summary {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--spacing-sm) var(--spacing-md);
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.article-page__summary dt {
  color: var(--color-text-secondary);
}

.article-page__summary dd {
  margin: 0;
}
</style>
