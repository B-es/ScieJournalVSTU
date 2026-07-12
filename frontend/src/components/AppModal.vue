<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

const props = defineProps<{ modelValue: boolean; title: string }>();
const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();

function close() {
  emit("update:modelValue", false);
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.modelValue) close();
}

onMounted(() => window.addEventListener("keydown", handleKeydown));
onUnmounted(() => window.removeEventListener("keydown", handleKeydown));
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal" role="dialog" aria-modal="true" :aria-label="title">
        <h3 class="modal__title">{{ title }}</h3>
        <div class="modal__body">
          <slot />
        </div>
        <div class="modal__actions">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(16, 24, 40, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 480px;
  width: 90%;
  padding: var(--spacing-lg);
}

.modal__title {
  margin: 0 0 var(--spacing-md);
}

.modal__body {
  margin-bottom: var(--spacing-lg);
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}
</style>
