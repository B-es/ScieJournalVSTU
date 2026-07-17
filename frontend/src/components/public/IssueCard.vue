<script setup lang="ts">
import type { PublicIssue } from "~/api/public";

const props = defineProps<{ issue: PublicIssue }>();

const { t, locale } = useI18n();

const description = computed(() => (locale.value === "en" ? props.issue.descriptionEn : props.issue.descriptionRu));
</script>

<template>
  <article class="issue-card">
    <img v-if="issue.coverImageUrl" :src="issue.coverImageUrl" alt="" class="issue-card__cover" />
    <div class="issue-card__body">
      <h3 class="issue-card__title">
        {{ t("issueCard.numberLabel", { n: issue.number }) }} ({{ issue.year }})
        <template v-if="issue.title"> — {{ issue.title }}</template>
      </h3>
      <p v-if="description" class="issue-card__description">{{ description }}</p>
      <div class="issue-card__counts">
        <span>{{ t("issueCard.articlesCount", { n: issue.articlesCount }) }}</span>
        <span>{{ t("issueCard.pagesCount", { n: issue.pagesCount }) }}</span>
        <span>{{ t("issueCard.authorsCount", { n: issue.authorsCount }) }}</span>
      </div>
      <div class="issue-card__actions">
        <NuxtLink :to="`/archive/${issue.id}`" class="btn btn--primary">{{ t("issueCard.openIssue") }}</NuxtLink>
      </div>
    </div>
  </article>
</template>

<style scoped>
.issue-card {
  display: flex;
  gap: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.issue-card__cover {
  width: 96px;
  height: 128px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.issue-card__body {
  flex: 1;
}

.issue-card__title {
  margin: 0 0 var(--spacing-sm);
  font-size: var(--type-h4-size, var(--type-body-size));
}

.issue-card__description {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm);
}

.issue-card__counts {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.btn {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}
</style>
