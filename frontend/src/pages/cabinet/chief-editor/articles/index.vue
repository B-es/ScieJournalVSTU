<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import * as articlesApi from "~/api/articles";
import ArticlesTable from "~/components/cabinet/ArticlesTable.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();

const items = ref<articlesApi.ArticleListItem[]>([]);
const loading = ref(true);
const error = ref("");
// Defaults to the actionable queue (DS "Управление статьями"); the filter
// dropdown still lets the chief editor browse other statuses.
const statusFilter = ref("submitted");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await articlesApi.listArticles(statusFilter.value || undefined);
    items.value = res.items;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

watch(statusFilter, load);
onMounted(load);
</script>

<template>
  <div>
    <h2>{{ t("chiefEditor.articlesQueueTitle") }}</h2>
    <ArticlesTable
      :items="items"
      :loading="loading"
      :error="error"
      :show-submit-action="false"
      :status-filter="statusFilter"
      detail-base-path="/cabinet/chief-editor/articles"
      @retry="load"
      @update:status-filter="statusFilter = $event"
    />
  </div>
</template>
