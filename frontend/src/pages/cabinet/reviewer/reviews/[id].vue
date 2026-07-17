<script setup lang="ts">
import { onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import * as reviewsApi from "~/api/reviews";
import ArticleReviewForm from "~/components/cabinet/ArticleReviewForm.vue";
import PdfViewer from "~/components/cabinet/PdfViewer.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const reviewId = route.params.id as string;

const review = ref<reviewsApi.ReviewItem | null>(null);
const manuscriptUrl = ref("");
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const { items } = await reviewsApi.listMyReviews();
    const found = items.find((i) => i.id === reviewId);
    if (!found) {
      error.value = t("reviewPage.notFound");
      return;
    }
    review.value = found;

    const detail = await articlesApi.getArticle(found.article.id);
    const version = detail.versions.find((v) => v.versionNumber === 1);
    manuscriptUrl.value = version?.manuscriptFileUrl ?? "";
  } catch {
    error.value = t("reviewPage.notFound");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <p v-else-if="error" role="alert">{{ error }}</p>

    <template v-else-if="review">
      <h2>{{ review.article.titleRu }}</h2>
      <p class="review-page__topic">{{ review.article.topic }}</p>
      <p class="review-page__abstract">{{ review.article.abstractRu }}</p>

      <PdfViewer v-if="manuscriptUrl" :file-url="manuscriptUrl" />

      <ArticleReviewForm
        :review-id="reviewId"
        :already-submitted="!!review.submittedAt"
        :existing-recommendation="review.recommendation"
        @submitted="load"
      />
    </template>
  </div>
</template>

<style scoped>
.review-page__topic {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
  margin: 0 0 var(--spacing-md);
}

.review-page__abstract {
  margin: 0 0 var(--spacing-lg);
}
</style>
