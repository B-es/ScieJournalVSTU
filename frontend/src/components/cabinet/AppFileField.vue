<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: File | null;
    label: string;
    accept?: string;
    required?: boolean;
    error?: string;
  }>(),
  { accept: undefined, required: false, error: "" },
);

const emit = defineEmits<{ "update:modelValue": [value: File | null] }>();

const fieldId = useId();

function handleChange(event: Event) {
  const input = event.target as HTMLInputElement;
  emit("update:modelValue", input.files?.[0] ?? null);
}
</script>

<template>
  <div class="file-field">
    <label :for="fieldId" class="file-field__label">
      {{ props.label }}
      <span v-if="props.required" class="file-field__required">— обязательное поле</span>
    </label>
    <input
      :id="fieldId"
      type="file"
      :accept="props.accept"
      class="file-field__input"
      :aria-invalid="!!props.error"
      @change="handleChange"
    >
    <p v-if="props.modelValue" class="file-field__filename">{{ props.modelValue.name }}</p>
    <p v-if="props.error" class="file-field__error" role="alert">{{ props.error }}</p>
  </div>
</template>

<style scoped>
.file-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.file-field__label {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.file-field__required {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.file-field__input {
  font-family: var(--font-family-base);
  font-size: var(--type-body-size);
}

.file-field__filename {
  margin: 0;
  font-size: var(--type-caption-size);
  color: var(--color-text-primary);
}

.file-field__error {
  margin: 0;
  font-size: var(--type-caption-size);
  color: var(--color-error);
}
</style>
