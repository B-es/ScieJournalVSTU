<script setup lang="ts">
const props = defineProps<{ page: number; pageSize: number; total: number }>();
const emit = defineEmits<{ "update:page": [value: number] }>();

const { t } = useI18n();

const totalPages = computed(() => Math.max(Math.ceil(props.total / props.pageSize), 1));
</script>

<template>
  <nav v-if="totalPages > 1" class="pagination" :aria-label="t('pagination.label')">
    <button type="button" class="btn btn--secondary" :disabled="page <= 1" @click="emit('update:page', page - 1)">
      {{ t("pagination.prev") }}
    </button>
    <span class="pagination__status">{{ t("pagination.pageOf", { page, total: totalPages }) }}</span>
    <button
      type="button"
      class="btn btn--secondary"
      :disabled="page >= totalPages"
      @click="emit('update:page', page + 1)"
    >
      {{ t("pagination.next") }}
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.pagination__status {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
