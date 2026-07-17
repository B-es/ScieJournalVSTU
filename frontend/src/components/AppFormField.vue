<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: string;
    label: string;
    type?: "text" | "email" | "password" | "textarea" | "date";
    error?: string;
    required?: boolean;
    autocomplete?: string;
  }>(),
  { type: "text", error: "", required: false, autocomplete: undefined },
);

defineEmits<{ "update:modelValue": [value: string] }>();

const fieldId = useId();
const errorId = `${fieldId}-error`;
</script>

<template>
  <div class="form-field">
    <label :for="fieldId" class="form-field__label">
      {{ label }}
      <span v-if="required" class="form-field__required">— обязательное поле</span>
    </label>
    <textarea
      v-if="props.type === 'textarea'"
      :id="fieldId"
      :value="props.modelValue"
      :required="props.required"
      class="form-field__input form-field__input--textarea"
      :class="{ 'form-field__input--error': !!props.error }"
      :aria-invalid="!!props.error"
      :aria-describedby="props.error ? errorId : undefined"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <input
      v-else
      :id="fieldId"
      :type="props.type"
      :value="props.modelValue"
      :required="props.required"
      :autocomplete="props.autocomplete"
      class="form-field__input"
      :class="{ 'form-field__input--error': !!props.error }"
      :aria-invalid="!!props.error"
      :aria-describedby="props.error ? errorId : undefined"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    >
    <p v-if="props.error" :id="errorId" class="form-field__error" role="alert">{{ props.error }}</p>
  </div>
</template>

<style scoped>
.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.form-field__label {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.form-field__required {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.form-field__input {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
  font-size: var(--type-body-size);
  color: var(--color-text-primary);
}

.form-field__input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-field__input--textarea {
  height: auto;
  min-height: 96px;
  padding: var(--spacing-sm);
  resize: vertical;
}

.form-field__input--error {
  border-color: var(--color-error);
}

.form-field__error {
  margin: 0;
  font-size: var(--type-caption-size);
  color: var(--color-error);
}
</style>
