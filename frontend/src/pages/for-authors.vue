<script setup lang="ts">
import { getJournalSettings, type PublicJournalSettings } from "~/api/public";

definePageMeta({ layout: "public" });

const { t, locale } = useI18n();
useSeoMeta({ title: `${t("forAuthorsPage.title")} — ${t("app.title")}` });

const settings = ref<PublicJournalSettings | null>(null);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    settings.value = await getJournalSettings();
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

const guidelines = computed(() =>
  settings.value ? (locale.value === "en" ? settings.value.guidelinesForAuthorsEn : settings.value.guidelinesForAuthorsRu) : "",
);

onMounted(load);
</script>

<template>
  <div>
    <h1>{{ t("forAuthorsPage.title") }}</h1>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="load">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="!guidelines" class="for-authors-page__empty">{{ t("forAuthorsPage.empty") }}</p>
    <p v-else class="for-authors-page__text">{{ guidelines }}</p>
  </div>
</template>

<style scoped>
.for-authors-page__text {
  white-space: pre-wrap;
}

.for-authors-page__empty {
  color: var(--color-text-secondary);
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
