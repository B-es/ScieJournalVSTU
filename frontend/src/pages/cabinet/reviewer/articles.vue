<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as reviewsApi from "~/api/reviews";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();

const items = ref<reviewsApi.ReviewItem[]>([]);
const loading = ref(true);
const error = ref("");

const acceptedItems = computed(() => items.value.filter((i) => i.invitationStatus === "accepted"));

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
    <h2>{{ t("reviewerCabinet.articlesTitle") }}</h2>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="load">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="!acceptedItems.length">{{ t("reviewerCabinet.articlesEmpty") }}</p>

    <ul v-else class="accepted-list">
      <li v-for="item in acceptedItems" :key="item.id">
        <strong>{{ item.article.titleRu }}</strong> — {{ item.article.topic }} ({{ t("topicCheck.deadline") }}: {{ item.deadline }})
      </li>
    </ul>
  </div>
</template>

<style scoped>
.accepted-list {
  list-style: none;
  padding: 0;
}

.accepted-list li {
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border);
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
