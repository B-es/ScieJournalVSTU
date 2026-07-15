<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as reviewsApi from "~/api/reviews";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";

const props = defineProps<{ articleId: string }>();
const emit = defineEmits<{ changed: [] }>();

const { t } = useI18n();

const items = ref<reviewsApi.ReviewItem[]>([]);
const candidates = ref<reviewsApi.ReviewerCandidate[]>([]);
const loading = ref(true);
const error = ref("");

const reassigningId = ref<string | null>(null);
const newReviewerId = ref("");
const newDeadline = ref("");
const reassignError = ref("");
const isSubmitting = ref(false);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [reviewsRes, candidatesRes] = await Promise.all([
      reviewsApi.listMyReviews(undefined, props.articleId),
      reviewsApi.listReviewerCandidates(),
    ]);
    items.value = reviewsRes.items;
    candidates.value = candidatesRes.items;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

onMounted(load);

function startReassign(reviewId: string) {
  reassigningId.value = reviewId;
  newReviewerId.value = "";
  newDeadline.value = "";
  reassignError.value = "";
}

function cancelReassign() {
  reassigningId.value = null;
}

async function submitReassign() {
  if (!newReviewerId.value || !newDeadline.value) {
    reassignError.value = t("auth.validation.required");
    return;
  }
  isSubmitting.value = true;
  reassignError.value = "";
  try {
    await reviewsApi.reassignReviewer(reassigningId.value as string, newReviewerId.value, newDeadline.value);
    reassigningId.value = null;
    await load();
    emit("changed");
  } catch (err) {
    reassignError.value = err instanceof ApiError ? err.message : t("common.error");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="reviewers-panel">
    <h3>{{ t("reviewersPanel.title") }}</h3>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error" role="alert">{{ error }}</p>
    <p v-else-if="!items.length">{{ t("reviewersPanel.empty") }}</p>

    <table v-else class="reviewers-panel__table">
      <thead>
        <tr>
          <th scope="col">{{ t("reviewersPanel.reviewer") }}</th>
          <th scope="col">{{ t("topicCheck.deadline") }}</th>
          <th scope="col">{{ t("articlesTable.columnStatus") }}</th>
          <th scope="col" />
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.reviewerFullName }} ({{ item.reviewerEmail }})</td>
          <td>{{ item.deadline }}</td>
          <td>
            <span :class="`reviewers-panel__status reviewers-panel__status--${item.invitationStatus}`">
              {{ t(`invitation.status.${item.invitationStatus}`) }}
            </span>
          </td>
          <td>
            <button
              v-if="item.invitationStatus === 'declined' && reassigningId !== item.id"
              type="button"
              class="btn btn--secondary"
              @click="startReassign(item.id)"
            >
              {{ t("reviewersPanel.reassign") }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="reassigningId" class="reviewers-panel__reassign-form">
      <h4>{{ t("reviewersPanel.reassignTitle") }}</h4>
      <label for="reassign-reviewer" class="reviewers-panel__select-label">{{ t("reviewersPanel.newReviewer") }}</label>
      <select id="reassign-reviewer" v-model="newReviewerId" class="reviewers-panel__select">
        <option value="" disabled>{{ t("reviewersPanel.newReviewerPlaceholder") }}</option>
        <option v-for="candidate in candidates" :key="candidate.id" :value="candidate.id">
          {{ candidate.fullName }} ({{ candidate.email }})
        </option>
      </select>
      <AppFormField v-model="newDeadline" type="date" :label="t('topicCheck.deadline')" required />

      <p v-if="reassignError" class="reviewers-panel__error" role="alert">{{ reassignError }}</p>

      <div class="reviewers-panel__actions">
        <button type="button" class="btn btn--secondary" @click="cancelReassign">
          {{ t("reviewersPanel.cancel") }}
        </button>
        <button type="button" class="btn btn--primary" :disabled="isSubmitting" @click="submitReassign">
          {{ isSubmitting ? t("common.loading") : t("reviewersPanel.reassignSubmit") }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reviewers-panel {
  margin-bottom: var(--spacing-lg);
}

.reviewers-panel__table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--spacing-md);
}

.reviewers-panel__table th {
  text-align: left;
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.reviewers-panel__table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.reviewers-panel__status {
  font-size: var(--type-caption-size);
  font-weight: 500;
}

.reviewers-panel__status--accepted {
  color: var(--color-success);
}

.reviewers-panel__status--declined {
  color: var(--color-error);
}

.reviewers-panel__status--invited {
  color: var(--color-text-secondary);
}

.reviewers-panel__status--cancelled {
  color: var(--color-text-secondary);
  text-decoration: line-through;
}

.reviewers-panel__reassign-form {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.reviewers-panel__select-label {
  display: block;
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.reviewers-panel__select {
  width: 100%;
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
  margin-bottom: var(--spacing-md);
}

.reviewers-panel__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.reviewers-panel__actions {
  display: flex;
  gap: var(--spacing-sm);
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
</style>