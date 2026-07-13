<script setup lang="ts">
import { getPublicArticle, type PublicArticleDetailResponse } from "~/api/public";
import PdfViewer from "~/components/cabinet/PdfViewer.vue";
import CitationBlock from "~/components/public/CitationBlock.vue";

definePageMeta({ layout: "public" });

const { t, locale } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<PublicArticleDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    detail.value = await getPublicArticle(articleId);
  } catch {
    error.value = t("publicArticlePage.notFound");
  } finally {
    loading.value = false;
  }
}

const title = computed(() => (detail.value ? (locale.value === "en" ? detail.value.article.titleEn : detail.value.article.titleRu) : ""));
const abstract = computed(() =>
  detail.value ? (locale.value === "en" ? detail.value.article.abstractEn : detail.value.article.abstractRu) : "",
);
const keywords = computed(() =>
  detail.value ? (locale.value === "en" ? detail.value.article.keywordsEn : detail.value.article.keywordsRu) : [],
);
const authorNames = computed(() => detail.value?.article.authors.map((a) => a.fullName).join(", ") ?? "");

onMounted(load);
watch(title, (value) => {
  if (value) useSeoMeta({ title: `${value} — ${t("app.title")}`, description: abstract.value });
});
</script>

<template>
  <div>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error" role="alert">{{ error }}</p>

    <template v-else-if="detail">
      <header class="public-article-page__header">
        <h1>{{ title }}</h1>
        <p v-if="authorNames" class="public-article-page__authors">{{ authorNames }}</p>
        <p v-if="detail.article.issueNumber" class="public-article-page__issue">
          {{ t("issuePage.numberLabel", { n: detail.article.issueNumber }) }} ({{ detail.article.issueYear }})
        </p>
      </header>

      <section class="public-article-page__section">
        <h2>{{ t("publicArticlePage.abstract") }}</h2>
        <p>{{ abstract }}</p>
      </section>

      <section v-if="keywords.length" class="public-article-page__section">
        <h2>{{ t("publicArticlePage.keywords") }}</h2>
        <ul class="public-article-page__keywords">
          <li v-for="kw in keywords" :key="kw">{{ kw }}</li>
        </ul>
      </section>

      <dl class="public-article-page__meta">
        <dt>{{ t("articlePage.doiLabel") }}</dt>
        <dd>{{ detail.article.doi }}</dd>
        <dt v-if="detail.article.pagesCount">{{ t("publicArticlePage.pages") }}</dt>
        <dd v-if="detail.article.pagesCount">{{ detail.article.pagesCount }}</dd>
      </dl>

      <PdfViewer v-if="detail.pdfUrl" :file-url="detail.pdfUrl" :confidential="false" />

      <CitationBlock :article-id="articleId" />
    </template>
  </div>
</template>

<style scoped>
.public-article-page__header {
  margin-bottom: var(--spacing-lg);
}

.public-article-page__authors {
  color: var(--color-text-secondary);
}

.public-article-page__issue {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
}

.public-article-page__section {
  margin-bottom: var(--spacing-lg);
}

.public-article-page__keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  list-style: none;
  padding: 0;
}

.public-article-page__keywords li {
  font-size: var(--type-caption-size);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 0 var(--spacing-xs);
}

.public-article-page__meta {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.public-article-page__meta dt {
  color: var(--color-text-secondary);
}

.public-article-page__meta dd {
  margin: 0;
}
</style>
