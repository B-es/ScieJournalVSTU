<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as reviewsApi from "~/api/reviews";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();

const items = ref<reviewsApi.ReviewItem[]>([]);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await reviewsApi.listMyReviews();
    items.value = res.items;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h2>{{ t("chiefEditor.invitationsTitle") }}</h2>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="load">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="!items.length">{{ t("chiefEditor.invitationsEmpty") }}</p>

    <table v-else class="invitations-table">
      <thead>
        <tr>
          <th scope="col">{{ t("articlesTable.columnTitle") }}</th>
          <th scope="col">{{ t("topicCheck.deadline") }}</th>
          <th scope="col">{{ t("articlesTable.columnStatus") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.article.titleRu }}</td>
          <td>{{ item.deadline }}</td>
          <td>
            <span :class="`invitation-status invitation-status--${item.invitationStatus}`">
              {{ t(`invitation.status.${item.invitationStatus}`) }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.invitations-table {
  width: 100%;
  border-collapse: collapse;
}

.invitations-table th {
  text-align: left;
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.invitations-table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.invitation-status {
  font-size: var(--type-caption-size);
  font-weight: 500;
}

.invitation-status--accepted {
  color: var(--color-success);
}

.invitation-status--declined {
  color: var(--color-error);
}

.invitation-status--invited {
  color: var(--color-text-secondary);
}

.btn--secondary {
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
}
</style>
