<script setup lang="ts">
withDefaults(defineProps<{ fileUrl: string; confidential?: boolean }>(), { confidential: true });

const { t } = useI18n();
</script>

<template>
  <div class="pdf-viewer">
    <div v-if="confidential" class="pdf-viewer__banner">{{ t("pdfViewer.confidential") }}</div>
    <iframe :src="fileUrl" class="pdf-viewer__frame" :title="t('pdfViewer.title')" />
    <p class="pdf-viewer__fallback">
      <a :href="fileUrl" target="_blank" rel="noopener">{{ t("pdfViewer.download") }}</a>
    </p>
  </div>
</template>

<style scoped>
.pdf-viewer {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
}

.pdf-viewer__banner {
  background: var(--color-warning);
  color: var(--color-text-primary);
  font-size: var(--type-caption-size);
  font-weight: 600;
  text-align: center;
  padding: var(--spacing-xs) var(--spacing-sm);
}

.pdf-viewer__frame {
  width: 100%;
  height: 600px;
  border: none;
  display: block;
}

.pdf-viewer__fallback {
  margin: 0;
  padding: var(--spacing-sm);
  background: var(--color-surface);
  font-size: var(--type-caption-size);
  text-align: center;
}
</style>
