<script setup lang="ts">
import { listPublicArticles, type PublicArticle } from "~/api/public";
import ArticleCard from "~/components/public/ArticleCard.vue";
import Pagination from "~/components/public/Pagination.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("searchPage.title")} — ${t("app.title")}` });

const PAGE_SIZE = 10;

const query = ref("");
const author = ref("");
const topic = ref("");
const page = ref(1);

const items = ref<PublicArticle[]>([]);
const total = ref(0);
const loading = ref(false);
const error = ref("");
const searched = ref(false);

async function search() {
  loading.value = true;
  error.value = "";
  searched.value = true;
  try {
    const res = await listPublicArticles({
      q: query.value || undefined,
      author: author.value || undefined,
      topic: topic.value || undefined,
      page: page.value,
      pageSize: PAGE_SIZE,
    });
    items.value = res.items;
    total.value = res.total;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

function onSubmit() {
  page.value = 1;
  search();
}

watch(page, search);
</script>

<template>
  <div>
    <h1>{{ t("searchPage.title") }}</h1>
    <br></br>
    <form class="search-form" @submit.prevent="onSubmit">
      <input v-model="query" type="text" class="search-form__input" :placeholder="t('searchPage.queryPlaceholder')" >
      <input v-model="author" type="text" class="search-form__input" :placeholder="t('searchPage.authorPlaceholder')" >
      <input v-model="topic" type="text" class="search-form__input" :placeholder="t('searchPage.topicPlaceholder')" >
      <button type="submit" class="btn btn--primary">{{ t("searchPage.submit") }}</button>
    </form>

    <p v-if="loading">{{ t("common.loading") }}</p>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary" @click="search">{{ t("common.retry") }}</button>
    </div>
    <p v-else-if="searched && !items.length">{{ t("searchPage.empty") }}</p>

    <template v-else-if="items.length">
      <div class="search-results">
        <ArticleCard v-for="article in items" :key="article.id" :article="article" />
      </div>
      <Pagination v-model:page="page" :page-size="PAGE_SIZE" :total="total" />
    </template>
  </div>
</template>

<style scoped>
.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.search-form__input {
  height: 40px;
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-base);
  flex: 1;
  min-width: 160px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.btn {
  display: inline-flex;
  align-items: center;
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
}

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}
</style>
