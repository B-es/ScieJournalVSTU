<script setup lang="ts">
import { getPublicIssue, type PublicIssueDetailResponse } from "~/api/public";
import ArticleCard from "~/components/public/ArticleCard.vue";

definePageMeta({ layout: "public" });

const { t, locale } = useI18n();
const route = useRoute();
const issueId = route.params.issueId as string;

const detail = ref<PublicIssueDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    detail.value = await getPublicIssue(issueId);
  } catch {
    error.value = t("issuePage.notFound");
  } finally {
    loading.value = false;
  }
}

const description = computed(() =>
  detail.value ? (locale.value === "en" ? detail.value.issue.descriptionEn : detail.value.issue.descriptionRu) : "",
);

onMounted(load);
watch(() => detail.value?.issue.title, (title) => {
  if (title !== undefined) useSeoMeta({ title: `${t("issuePage.numberLabel", { n: detail.value!.issue.number })} — ${t("app.title")}` });
});
</script>

<template>
  <div>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error" role="alert">{{ error }}</p>

    <template v-else-if="detail">
      <header class="issue-page__header">
        <img v-if="detail.issue.coverImageUrl" :src="detail.issue.coverImageUrl" alt="" class="issue-page__cover" >
        <div>
          <h1>{{ t("issuePage.numberLabel", { n: detail.issue.number }) }} ({{ detail.issue.year }})</h1>
          <p v-if="detail.issue.title">{{ detail.issue.title }}</p>
          <p v-if="description" class="issue-page__description">{{ description }}</p>
        </div>
      </header>

      <h2>{{ t("issuePage.contents") }}</h2>
      <p v-if="!detail.articles.length">{{ t("issuePage.empty") }}</p>
      <div v-else class="issue-page__articles">
        <ArticleCard v-for="article in detail.articles" :key="article.id" :article="article" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.issue-page__header {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.issue-page__cover {
  width: 160px;
  height: 220px;
  object-fit: cover;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.issue-page__description {
  color: var(--color-text-secondary);
}

.issue-page__articles {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
</style>
