<script setup lang="ts">
import { getCitation } from "~/api/public";

const props = defineProps<{ articleId: string }>();

const { t } = useI18n();

const FORMATS = ["gost", "apa", "bibtex"] as const;
type Format = (typeof FORMATS)[number];

const selectedFormat = ref<Format>("gost");
const citationText = ref("");
const loading = ref(false);
const error = ref("");
const copyAnnouncement = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getCitation(props.articleId, selectedFormat.value);
    citationText.value = res.citationText;
  } catch {
    error.value = t("citation.error");
  } finally {
    loading.value = false;
  }
}

async function copyText() {
  try {
    await navigator.clipboard.writeText(citationText.value);
    copyAnnouncement.value = t("citation.copied");
  } catch {
    copyAnnouncement.value = t("citation.copyError");
  }
}

watch(selectedFormat, load);
onMounted(load);
</script>

<template>
  <section class="citation-block">
    <h3>{{ t("citation.title") }}</h3>
    <div class="citation-block__formats" role="group" :aria-label="t('citation.title')">
      <button
        v-for="fmt in FORMATS"
        :key="fmt"
        type="button"
        class="citation-block__format-btn"
        :class="{ active: selectedFormat === fmt }"
        @click="selectedFormat = fmt"
      >
        {{ t(`citation.format.${fmt}`) }}
      </button>
    </div>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error">{{ error }}</p>
    <template v-else>
      <pre class="citation-block__text">{{ citationText }}</pre>
      <button type="button" class="btn btn--secondary" @click="copyText">{{ t("citation.copy") }}</button>
    </template>

    <p class="visually-hidden" aria-live="polite">{{ copyAnnouncement }}</p>
  </section>
</template>

<style scoped>
.citation-block {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.citation-block__formats {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.citation-block__format-btn {
  height: 32px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.citation-block__format-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.citation-block__text {
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm);
  font-family: inherit;
  margin: 0 0 var(--spacing-sm);
}

.btn {
  display: inline-flex;
  align-items: center;
  height: 36px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-primary);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}
</style>
