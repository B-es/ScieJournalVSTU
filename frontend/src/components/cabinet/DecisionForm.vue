<script setup lang="ts">
import { computed, ref } from "vue";
import type { ArticleReviewSummary, DecisionPayload } from "~/api/articles";
import * as articlesApi from "~/api/articles";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";
import AppModal from "~/components/AppModal.vue";

const props = defineProps<{ articleId: string; reviews: ArticleReviewSummary[] }>();
const emit = defineEmits<{ decided: [] }>();

const { t } = useI18n();

const acceptedReviews = computed(() => props.reviews.filter((r) => r.invitationStatus === "accepted"));
const submittedCount = computed(() => acceptedReviews.value.filter((r) => r.submittedAt).length);
const ready = computed(() => acceptedReviews.value.length > 0 && submittedCount.value === acceptedReviews.value.length);

const decision = ref<DecisionPayload["decision"] | "">("");
const comment = ref("");
const fieldError = ref("");
const formError = ref("");
const isSubmitting = ref(false);
const showRejectConfirm = ref(false);

function validate(): boolean {
  if (!decision.value) {
    fieldError.value = t("auth.validation.required");
    return false;
  }
  if (!comment.value.trim()) {
    fieldError.value = t("auth.validation.required");
    return false;
  }
  fieldError.value = "";
  return true;
}

function handleSubmitClick() {
  formError.value = "";
  if (!validate()) return;

  if (decision.value === "reject") {
    showRejectConfirm.value = true;
    return;
  }
  submitDecision();
}

async function submitDecision() {
  showRejectConfirm.value = false;
  isSubmitting.value = true;
  try {
    await articlesApi.makeDecision(props.articleId, {
      decision: decision.value as DecisionPayload["decision"],
      comment: comment.value,
    });
    emit("decided");
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t("decisionForm.error");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="decision-form">
    <h3>{{ t("decisionForm.title") }}</h3>

    <h4>{{ t("decisionForm.reviewsTitle") }}</h4>
    <ul class="decision-form__reviews">
      <li v-for="review in reviews" :key="review.id">
        <template v-if="review.submittedAt">
          <strong>{{ t(`decisionForm.recommendation.${review.recommendation}`) }}</strong>
          <p v-if="review.commentsForAuthor">{{ review.commentsForAuthor }}</p>
        </template>
        <em v-else>{{ t("decisionForm.notSubmittedYet") }}</em>
      </li>
    </ul>

    <p v-if="!ready" class="decision-form__waiting">
      {{ t("decisionForm.waiting", { submitted: submittedCount, total: acceptedReviews.length }) }}
    </p>

    <template v-else>
      <div class="decision-form__field">
        <label for="decision">{{ t("decisionForm.decisionLabel") }}</label>
        <select id="decision" v-model="decision" class="decision-form__select">
          <option value="" disabled>{{ t("decisionForm.decisionPlaceholder") }}</option>
          <option value="accept">{{ t("decisionForm.recommendation.accept") }}</option>
          <option value="revise">{{ t("decisionForm.recommendation.revise") }}</option>
          <option value="reject">{{ t("decisionForm.recommendation.reject") }}</option>
        </select>
      </div>

      <AppFormField v-model="comment" type="textarea" :label="t('decisionForm.comment')" required />

      <p v-if="fieldError" class="decision-form__error" role="alert">{{ fieldError }}</p>
      <p v-if="formError" class="decision-form__error" role="alert" aria-live="assertive">{{ formError }}</p>

      <button type="button" class="btn btn--primary" :disabled="isSubmitting" @click="handleSubmitClick">
        {{ isSubmitting ? t("common.loading") : t("decisionForm.submit") }}
      </button>
    </template>

    <AppModal v-model="showRejectConfirm" :title="t('decisionForm.confirmRejectTitle')">
      <p>{{ t("decisionForm.confirmRejectBody") }}</p>
      <template #actions>
        <button type="button" class="btn btn--secondary" @click="showRejectConfirm = false">
          {{ t("decisionForm.cancel") }}
        </button>
        <button type="button" class="btn btn--danger" @click="submitDecision">
          {{ t("decisionForm.confirmRejectButton") }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.decision-form__reviews {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--spacing-md);
}

.decision-form__reviews li {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-sm);
}

.decision-form__waiting {
  color: var(--color-warning);
  font-weight: 600;
}

.decision-form__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.decision-form__field label {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.decision-form__select {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
}

.decision-form__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.btn {
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
}

.btn--primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.btn--danger {
  background: var(--color-error);
  color: var(--color-text-inverse);
  border: none;
}
</style>
