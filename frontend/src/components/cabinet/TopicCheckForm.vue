<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import * as reviewsApi from "~/api/reviews";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";

const props = defineProps<{ articleId: string }>();
const emit = defineEmits<{ done: [] }>();

const { t } = useI18n();

const mode = ref<"approve" | "reject">("approve");
const comment = ref("");
const deadline = ref("");
const selectedReviewerIds = ref<string[]>([]);
const candidates = ref<reviewsApi.ReviewerCandidate[]>([]);

const fieldError = ref("");
const formError = ref("");
const isSubmitting = ref(false);

onMounted(async () => {
  try {
    const res = await reviewsApi.listReviewerCandidates();
    candidates.value = res.items;
  } catch {
    formError.value = t("common.error");
  }
});

function toggleReviewer(id: string) {
  const idx = selectedReviewerIds.value.indexOf(id);
  if (idx === -1) selectedReviewerIds.value.push(id);
  else selectedReviewerIds.value.splice(idx, 1);
}

async function handleSubmit() {
  formError.value = "";
  fieldError.value = "";

  if (mode.value === "reject") {
    if (!comment.value.trim()) {
      fieldError.value = t("topicCheck.commentRequired");
      return;
    }
    isSubmitting.value = true;
    try {
      await articlesApi.topicCheck(props.articleId, { approved: false, comment: comment.value });
      emit("done");
    } catch {
      formError.value = t("topicCheck.error");
    } finally {
      isSubmitting.value = false;
    }
    return;
  }

  if (selectedReviewerIds.value.length < 2) {
    fieldError.value = t("topicCheck.reviewersMinError");
    return;
  }
  if (!deadline.value) {
    fieldError.value = t("auth.validation.required");
    return;
  }

  isSubmitting.value = true;
  try {
    await articlesApi.topicCheck(props.articleId, { approved: true });
    await articlesApi.assignReviewers(props.articleId, {
      reviewerIds: selectedReviewerIds.value,
      deadline: deadline.value,
    });
    emit("done");
  } catch (err) {
    if (err instanceof ApiError && err.fieldErrors?.reviewerIds) {
      fieldError.value = err.fieldErrors.reviewerIds[0];
    } else {
      formError.value = t("topicCheck.error");
    }
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="topic-check-form">
    <h3>{{ t("topicCheck.title") }}</h3>

    <div class="topic-check-form__mode">
      <label>
        <input v-model="mode" type="radio" value="approve" >
        {{ t("topicCheck.approveAndAssign") }}
      </label>
      <label>
        <input v-model="mode" type="radio" value="reject" >
        {{ t("topicCheck.reject") }}
      </label>
    </div>

    <AppFormField v-if="mode === 'reject'" v-model="comment" type="textarea" :label="t('topicCheck.comment')" required />

    <template v-else>
      <h4>{{ t("topicCheck.reviewersTitle") }}</h4>
      <ul class="topic-check-form__reviewers">
        <li v-for="candidate in candidates" :key="candidate.id">
          <label>
            <input
              type="checkbox"
              :checked="selectedReviewerIds.includes(candidate.id)"
              @change="toggleReviewer(candidate.id)"
            >
            {{ candidate.fullName }} ({{ candidate.email }})
          </label>
        </li>
      </ul>
      <AppFormField v-model="deadline" type="date" :label="t('topicCheck.deadline')" required />
    </template>

    <p v-if="fieldError" class="topic-check-form__error" role="alert">{{ fieldError }}</p>
    <p v-if="formError" class="topic-check-form__error" role="alert">{{ formError }}</p>

    <button type="button" class="btn btn--primary" :disabled="isSubmitting" @click="handleSubmit">
      {{ isSubmitting ? t("common.loading") : mode === "reject" ? t("topicCheck.reject") : t("topicCheck.submit") }}
    </button>
  </div>
</template>

<style scoped>
.topic-check-form__mode {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

.topic-check-form__reviewers {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--spacing-md);
}

.topic-check-form__reviewers li {
  margin-bottom: var(--spacing-xs);
}

.topic-check-form__error {
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

.btn--primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
