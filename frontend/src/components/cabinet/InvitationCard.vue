<script setup lang="ts">
import { computed, ref } from "vue";
import type { ReviewItem } from "~/api/reviews";
import * as reviewsApi from "~/api/reviews";
import { ApiError } from "~/api/http";

const props = defineProps<{ review: ReviewItem }>();
const emit = defineEmits<{ responded: [] }>();

const { t } = useI18n();

const isSubmitting = ref(false);
const error = ref("");

const daysLeft = computed(() => {
  const deadline = new Date(props.review.deadline);
  const today = new Date();
  deadline.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  return Math.round((deadline.getTime() - today.getTime()) / 86400000);
});

const urgency = computed<"normal" | "warning" | "overdue">(() => {
  if (daysLeft.value < 0) return "overdue";
  if (daysLeft.value <= 2) return "warning";
  return "normal";
});

async function respond(accepted: boolean) {
  error.value = "";
  isSubmitting.value = true;
  try {
    await reviewsApi.respondToInvitation(props.review.id, accepted);
    emit("responded");
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : t("invitation.error");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <article class="invitation-card">
    <h3 class="invitation-card__title">{{ review.article.titleRu }}</h3>
    <p class="invitation-card__topic">{{ review.article.topic }}</p>
    <p class="invitation-card__abstract">{{ review.article.abstractRu }}</p>

    <p class="invitation-card__deadline" :class="`invitation-card__deadline--${urgency}`">
      {{ t("invitation.deadline") }}: {{ review.deadline }}
      <span v-if="urgency === 'overdue'">— {{ t("invitation.overdue") }}</span>
      <span v-else-if="urgency === 'warning'">— {{ t("invitation.daysLeft", { n: daysLeft }) }}</span>
    </p>

    <p v-if="error" class="invitation-card__error" role="alert">{{ error }}</p>

    <div v-if="review.invitationStatus === 'invited'" class="invitation-card__actions">
      <button type="button" class="btn btn--primary" :disabled="isSubmitting" @click="respond(true)">
        {{ t("invitation.accept") }}
      </button>
      <button type="button" class="btn btn--secondary" :disabled="isSubmitting" @click="respond(false)">
        {{ t("invitation.decline") }}
      </button>
    </div>
    <p v-else class="invitation-card__processed">{{ t(`invitation.status.${review.invitationStatus}`) }}</p>
  </article>
</template>

<style scoped>
.invitation-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  background: var(--color-surface);
}

.invitation-card__title {
  margin: 0 0 var(--spacing-xs);
}

.invitation-card__topic {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
  margin: 0 0 var(--spacing-sm);
}

.invitation-card__abstract {
  margin: 0 0 var(--spacing-sm);
}

.invitation-card__deadline {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm);
}

.invitation-card__deadline--warning {
  color: var(--color-warning);
  font-weight: 600;
}

.invitation-card__deadline--overdue {
  color: var(--color-error);
  font-weight: 600;
}

.invitation-card__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.invitation-card__actions {
  display: flex;
  gap: var(--spacing-sm);
}

.invitation-card__processed {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
  font-weight: 500;
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

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
