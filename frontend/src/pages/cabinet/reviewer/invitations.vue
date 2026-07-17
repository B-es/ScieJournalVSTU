<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as reviewsApi from "~/api/reviews";
import InvitationCard from "~/components/cabinet/InvitationCard.vue";

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
    <h2>{{ t("reviewerCabinet.invitationsTitle") }}</h2>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="load">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="!items.length">{{ t("reviewerCabinet.invitationsEmpty") }}</p>

    <InvitationCard v-for="item in items" :key="item.id" :review="item" @responded="load" />
  </div>
</template>

<style scoped>
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
