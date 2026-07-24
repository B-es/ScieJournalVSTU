<script setup lang="ts">
import { ref } from "vue";
import * as reviewsApi from "~/api/reviews";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";
import AppFileField from "~/components/cabinet/AppFileField.vue";
import ReviewEvaluationForm from "~/components/cabinet/ReviewEvaluationForm.vue";

const props = defineProps<{
  reviewId: string;
  alreadySubmitted: boolean;
  existingRecommendation?: string;
}>();
const emit = defineEmits<{ submitted: [] }>();

const { t } = useI18n();

const recommendation = ref<"accept" | "revise" | "reject" | "">("");
const commentsForAuthor = ref("");
const commentsForEditor = ref("");
const reviewFile = ref<File | null>(null);

const fieldErrors = ref<Record<string, string>>({});
const formError = ref("");
const isSubmitting = ref(false);

const evaluationData = ref({
  evaluationRating: {
    introduction: "",
    research_design: "",
    methods: "",
    results: "",
    conclusions: "",
    figures_tables: "",
  },
  languageQuality: "",
  conflictOfInterest: null as boolean | null,
  plagiarismDetected: null as boolean | null,
  ethicalIssues: null as boolean | null,
  articleRating: {
    originality: "",
    significance: "",
    presentation: "",
    scientific_validity: "",
    reader_interest: "",
  },
});

async function handleSubmit() {
  formError.value = "";
  fieldErrors.value = {};

  if (!recommendation.value) {
    fieldErrors.value.recommendation = t("auth.validation.required");
    return;
  }
  if (!commentsForAuthor.value.trim()) {
    fieldErrors.value.commentsForAuthor = t("auth.validation.required");
    return;
  }

  isSubmitting.value = true;
  try {
    await reviewsApi.submitReview(props.reviewId, {
      recommendation: recommendation.value,
      formData: {
        commentsForAuthor: commentsForAuthor.value,
        commentsForEditor: commentsForEditor.value,
      },
      reviewFile: reviewFile.value ?? undefined,
      evaluationRating: evaluationData.value.evaluationRating,
      languageQuality: evaluationData.value.languageQuality,
      conflictOfInterest: evaluationData.value.conflictOfInterest,
      plagiarismDetected: evaluationData.value.plagiarismDetected,
      ethicalIssues: evaluationData.value.ethicalIssues,
      articleRating: evaluationData.value.articleRating,
    });
    emit("submitted");
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t("reviewForm.error");
  } finally {
    isSubmitting.value = false;
  }
  
  const requiredRatingFields = ["originality", "significance", "presentation", "scientific_validity", "reader_interest"];
  for (const field of requiredRatingFields) {
    if (!evaluationData.value.articleRating[field]) {
      fieldErrors.value.rating = t("reviewForm.ratingRequired");
      return;
    }
  }
  
  if (evaluationData.value.conflictOfInterest === null) {
    fieldErrors.value.conflict = t("reviewForm.conflictRequired");
    return;
  }
  if (evaluationData.value.plagiarismDetected === null) {
    fieldErrors.value.plagiarism = t("reviewForm.plagiarismRequired");
    return;
  }
  if (evaluationData.value.ethicalIssues === null) {
    fieldErrors.value.ethical = t("reviewForm.ethicalRequired");
    return;
  }

  isSubmitting.value = true;
  try {
    await reviewsApi.submitReview(props.reviewId, {
      recommendation: recommendation.value,
      formData: {
        commentsForAuthor: commentsForAuthor.value,
        commentsForEditor: commentsForEditor.value,
      },
      reviewFile: reviewFile.value ?? undefined,
      evaluationRating: evaluationData.value.evaluationRating,
      languageQuality: evaluationData.value.languageQuality,
      conflictOfInterest: evaluationData.value.conflictOfInterest,
      plagiarismDetected: evaluationData.value.plagiarismDetected,
      ethicalIssues: evaluationData.value.ethicalIssues,
      articleRating: evaluationData.value.articleRating,
    });
    emit("submitted");
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t("reviewForm.error");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="review-form">
    <template v-if="alreadySubmitted">
      <p class="review-form__done">
        {{ t("reviewForm.alreadySubmitted") }}
        <strong v-if="existingRecommendation">{{ t(`reviewForm.recommendation.${existingRecommendation}`) }}</strong>
      </p>
    </template>

    <template v-else>
      <h3>{{ t("reviewForm.title") }}</h3>

      <ReviewEvaluationForm v-model="evaluationData" />

      <p v-if="fieldErrors.evaluation" class="review-form__error" role="alert">
        {{ fieldErrors.evaluation }}
      </p>

      <div class="review-form__field">
        <label for="recommendation">{{ t("reviewForm.recommendationLabel") }}</label>
        <select id="recommendation" v-model="recommendation" class="review-form__select">
          <option value="" disabled>{{ t("reviewForm.recommendationPlaceholder") }}</option>
          <option value="accept">{{ t("reviewForm.recommendation.accept") }}</option>
          <option value="revise">{{ t("reviewForm.recommendation.revise") }}</option>
          <option value="reject">{{ t("reviewForm.recommendation.reject") }}</option>
        </select>
        <p v-if="fieldErrors.recommendation" class="review-form__error" role="alert">{{ fieldErrors.recommendation }}</p>
      </div>

      <AppFormField
        v-model="commentsForAuthor"
        type="textarea"
        :label="t('reviewForm.commentsForAuthor')"
        required
        :error="fieldErrors.commentsForAuthor"
      />
      <AppFormField v-model="commentsForEditor" type="textarea" :label="t('reviewForm.commentsForEditor')" />
      <AppFileField v-model="reviewFile" :label="t('reviewForm.reviewFile')" />

      <p v-if="formError" class="review-form__error" role="alert" aria-live="assertive">{{ formError }}</p>

      <button type="button" class="btn btn--primary" :disabled="isSubmitting" @click="handleSubmit">
        {{ isSubmitting ? t("common.loading") : t("reviewForm.submit") }}
      </button>
    </template>
  </div>
</template>

<style scoped>
.review-form__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.review-form__field label {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.review-form__select {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
}

.review-form__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.review-form__done {
  color: var(--color-text-secondary);
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

.btn--primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
