<script setup lang="ts">
import type { ArticleListItem } from "~/api/articles";
import StatusBadge from "~/components/StatusBadge.vue";

withDefaults(
  defineProps<{
    items: ArticleListItem[];
    loading?: boolean;
    error?: string;
  }>(),
  { loading: false, error: "" },
);

const emit = defineEmits<{ retry: []; "update:statusFilter": [value: string] }>();

const { t } = useI18n();

const STATUS_OPTIONS = ["draft", "submitted", "needs_revision", "rejected", "in_review", "accepted", "published"];

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString();
}
</script>

<template>
  <div class="articles-table">
    <div class="articles-table__toolbar">
      <select class="articles-table__filter" @change="emit('update:statusFilter', ($event.target as HTMLSelectElement).value)">
        <option value="">{{ t("articlesTable.filterAll") }}</option>
        <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ t(`articleStatus.${s}`) }}</option>
      </select>
      <NuxtLink to="/cabinet/author/submit" class="btn btn--primary">{{ t("articlesTable.submitButton") }}</NuxtLink>
    </div>

    <p v-if="loading" class="articles-table__state">{{ t("common.loading") }}</p>

    <div v-else-if="error" class="articles-table__state">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="emit('retry')">{{ t("common.retry") }}</button>
    </div>

    <div v-else-if="!items.length" class="articles-table__state">
      <p>{{ t("articlesTable.empty") }}</p>
      <NuxtLink to="/cabinet/author/submit" class="btn btn--primary">{{ t("articlesTable.emptyCta") }}</NuxtLink>
    </div>

    <table v-else class="articles-table__table">
      <thead>
        <tr>
          <th scope="col">{{ t("articlesTable.columnTitle") }}</th>
          <th scope="col">{{ t("articlesTable.columnStatus") }}</th>
          <th scope="col">{{ t("articlesTable.columnDate") }}</th>
          <th scope="col">{{ t("articlesTable.columnAction") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.titleRu || item.titleEn || "—" }}</td>
          <td><StatusBadge :status="(item.status as any)" /></td>
          <td>{{ formatDate(item.createdAt) }}</td>
          <td><NuxtLink :to="`/cabinet/author/articles/${item.id}`">{{ t("articlesTable.open") }}</NuxtLink></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.articles-table__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.articles-table__filter {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
}

.articles-table__state {
  padding: var(--spacing-xl) 0;
  text-align: center;
  color: var(--color-text-secondary);
}

.articles-table__table {
  width: 100%;
  border-collapse: collapse;
}

.articles-table__table th {
  text-align: left;
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.articles-table__table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
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

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}
</style>
