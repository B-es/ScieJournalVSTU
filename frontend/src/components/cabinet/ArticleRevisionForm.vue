<script setup lang="ts">
import { ref } from "vue";
import * as articlesApi from "~/api/articles";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";
import AppFileField from "~/components/cabinet/AppFileField.vue";

const props = defineProps<{ articleId: string }>();
const emit = defineEmits<{ uploaded: [] }>();

const { t } = useI18n();

const manuscriptFile = ref<File | null>(null);
const authorComment = ref("");
const fieldError = ref("");
const formError = ref("");
const isSubmitting = ref(false);

async function handleSubmit() {
  formError.value = "";
  fieldError.value = "";

  if (!manuscriptFile.value) {
    fieldError.value = t("auth.validation.required");
    return;
  }

  isSubmitting.value = true;
  try {
    await articlesApi.uploadRevisionVersion(props.articleId, {
      manuscriptFile: manuscriptFile.value,
      authorComment: authorComment.value,
    });
    emit("uploaded");
  } catch (err) {
    if (err instanceof ApiError && err.fieldErrors?.manuscriptFile) {
      fieldError.value = err.fieldErrors.manuscriptFile[0];
    } else {
      formError.value = t("articleRevision.error");
    }
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="revision-form">
    <h3>{{ t("articleRevision.title") }}</h3>

    <AppFileField
      v-model="manuscriptFile"
      :label="t('articleForm.manuscriptFile')"
      accept=".doc,.docx,.pdf"
      required
      :error="fieldError"
    />
    <AppFormField v-model="authorComment" type="textarea" :label="t('articleRevision.authorComment')" />

    <p v-if="formError" class="revision-form__error" role="alert" aria-live="assertive">{{ formError }}</p>

    <button
      type="button"
      class="btn btn--primary"
      :disabled="isSubmitting"
      :aria-disabled="isSubmitting"
      @click="handleSubmit"
    >
      {{ isSubmitting ? t("common.loading") : t("articleRevision.submit") }}
    </button>
  </div>
</template>

<style scoped>
.revision-form__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.btn--primary {
  height: 40px;
  padding: 0 var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
}

.btn--primary[aria-disabled="true"] {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
