<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import ArticlesTable from "~/components/cabinet/ArticlesTable.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();

const items = ref<articlesApi.ArticleListItem[]>([]);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    // DS: this screen lists in_review articles regardless of whether every
    // review is in yet — the ones not fully reviewed show the "Ожидаем
    // рецензию от N из M" empty state on the detail page instead of a
    // disabled queue entry here (M3e plan decision #8).
    const res = await articlesApi.listArticles("in_review");
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
    <h2>{{ t("cabinet.nav.decisions") }}</h2>
    <br></br>
    <ArticlesTable
      :items="items"
      :loading="loading"
      :error="error"
      :show-submit-action="false"
      detail-base-path="/cabinet/chief-editor/articles"
      @retry="load"
    />
  </div>
</template>
