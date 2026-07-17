<script setup lang="ts">
import type { PublicArticle } from "~/api/public";

const props = defineProps<{ article: PublicArticle }>();

const { t, locale } = useI18n();

const title = computed(() => (locale.value === "en" ? props.article.titleEn : props.article.titleRu));
const keywords = computed(() => (locale.value === "en" ? props.article.keywordsEn : props.article.keywordsRu));
const authorNames = computed(() => props.article.authors.map((a) => a.fullName).join(", "));
</script>

<template>
  <article class="article-card">
    <div class="article-card__header">
      <NuxtLink :to="`/article/${article.id}`" class="article-card__title">{{ title }}</NuxtLink>
      <span class="article-card__oa-badge">{{ t("articleCard.openAccess") }}</span>
    </div>
    <p v-if="authorNames" class="article-card__authors">{{ authorNames }}</p>
    <ul v-if="keywords.length" class="article-card__keywords">
      <li v-for="kw in keywords" :key="kw">{{ kw }}</li>
    </ul>
    <div class="article-card__meta">
      <span v-if="article.pagesCount">{{ t("articleCard.pages", { n: article.pagesCount }) }}</span>
      <span v-if="article.doi">DOI: {{ article.doi }}</span>
    </div>
  </article>
</template>

<style scoped>
.article-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.article-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.article-card__title {
  font-size: var(--type-h4-size, var(--type-body-size));
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
}

.article-card__title:hover {
  text-decoration: underline;
}

.article-card__oa-badge {
  flex-shrink: 0;
  font-size: var(--type-caption-size);
  font-weight: 500;
  color: var(--color-success);
  border: 1px solid var(--color-success);
  border-radius: var(--radius-sm);
  padding: 0 var(--spacing-xs);
  white-space: nowrap;
}

.article-card__authors {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm);
}

.article-card__keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  list-style: none;
  padding: 0;
  margin: 0 0 var(--spacing-sm);
}

.article-card__keywords li {
  font-size: var(--type-caption-size);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 0 var(--spacing-xs);
}

.article-card__meta {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}
</style>
