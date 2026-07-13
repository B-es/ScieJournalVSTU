<script setup lang="ts">
import { listPublicIssues, type PublicIssue } from "~/api/public";
import IssueCard from "~/components/public/IssueCard.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("archivePage.title")} — ${t("app.title")}` });

const issues = ref<PublicIssue[]>([]);
const yearFilter = ref("");
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const year = yearFilter.value ? Number(yearFilter.value) : undefined;
    const res = await listPublicIssues(year);
    issues.value = res.items;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

const years = computed(() => {
  const set = new Set(issues.value.map((i) => i.year));
  return Array.from(set).sort((a, b) => b - a);
});

onMounted(load);
watch(yearFilter, load);
</script>

<template>
  <div>
    <h1>{{ t("archivePage.title") }}</h1>

    <div class="archive-toolbar">
      <select v-model="yearFilter" class="archive-toolbar__filter">
        <option value="">{{ t("archivePage.allYears") }}</option>
        <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
      </select>
    </div>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="load">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="!issues.length">{{ t("archivePage.empty") }}</p>
    <div v-else class="archive-list">
      <IssueCard v-for="issue in issues" :key="issue.id" :issue="issue" />
    </div>
  </div>
</template>

<style scoped>
.archive-toolbar {
  margin-bottom: var(--spacing-md);
}

.archive-toolbar__filter {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
}

.archive-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.btn {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-primary);
}
</style>
