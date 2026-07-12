<script setup lang="ts">
import ArticleSubmitForm from "~/components/cabinet/ArticleSubmitForm.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();

async function handleSubmitted(articleId: string) {
  await navigateTo(`/cabinet/author/articles/${articleId}`);
}
</script>

<template>
  <div>
    <h2>{{ t("cabinet.nav.submitArticle") }}</h2>
    <ArticleSubmitForm @submitted="handleSubmitted" />
  </div>
</template>
