<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import * as articlesApi from "~/api/articles";
import ArticleRevisionForm from "~/components/cabinet/ArticleRevisionForm.vue";
import ArticleSubmitForm from "~/components/cabinet/ArticleSubmitForm.vue";
import StatusBadge from "~/components/StatusBadge.vue";

definePageMeta({ layout: "cabinet" });

const { t } = useI18n();
const route = useRoute();
const articleId = route.params.id as string;

const detail = ref<articlesApi.ArticleDetailResponse | null>(null);
const loading = ref(true);
const error = ref("");

function latestDecision(decision: "revise" | "reject" | "accept") {
  const decisions = detail.value?.decisions ?? [];
  const matches = decisions
    .filter((d) => d.decision === decision)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  return matches[0];
}

// Any stage can send an article to revision now (completeness check, M3b —
// the technical editor; review decision, M3e — the chief editor) — track
// which stage it came from so the right role gets credited in the label.
const latestRevision = computed(() => latestDecision("revise"));
const latestRevisionComment = computed(() => latestRevision.value?.comment ?? "");
const revisionCommentLabel = computed(() =>
  latestRevision.value?.stage === "completeness_check" ? t("articlePage.techEditorComment") : t("articlePage.editorComment"),
);
const latestRejectionComment = computed(() => latestDecision("reject")?.comment ?? "");
const latestAcceptanceComment = computed(() => latestDecision("accept")?.comment ?? "");

const reviewerComments = computed(() => (detail.value?.reviews ?? []).map((r) => r.commentsForAuthor).filter(Boolean));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    detail.value = await articlesApi.getArticle(articleId);
  } catch {
    error.value = t("articlePage.notFound");
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

    <template v-else-if="detail">
      <header class="article-page__header">
        <h2>{{ detail.article.titleRu }}</h2>
        <StatusBadge :status="(detail.article.status as any)" />
      </header>

      <section v-if="detail.article.status === 'draft'">
        <ArticleSubmitForm :article-id="articleId" @submitted="load" />
      </section>

      <section v-else>
        <p v-if="detail.article.status === 'needs_revision' && latestRevisionComment" class="article-page__notice">
          <strong>{{ revisionCommentLabel }}:</strong> {{ latestRevisionComment }}
        </p>
        <template v-else-if="detail.article.status === 'rejected'">
          <p class="article-page__notice article-page__notice--rejected">{{ t("articlePage.rejectedNotice") }}</p>
          <p v-if="latestRejectionComment" class="article-page__notice">
            <strong>{{ t("articlePage.editorComment") }}:</strong> {{ latestRejectionComment }}
          </p>
        </template>
        <template v-else-if="detail.article.status === 'accepted'">
          <p class="article-page__notice article-page__notice--accepted">{{ t("articlePage.acceptedNotice") }}</p>
          <p v-if="latestAcceptanceComment" class="article-page__notice">
            <strong>{{ t("articlePage.editorComment") }}:</strong> {{ latestAcceptanceComment }}
          </p>
        </template>
        <template v-else-if="detail.article.status === 'published'">
          <p class="article-page__notice article-page__notice--accepted">{{ t("articlePage.publishedNotice") }}</p>
          <p class="article-page__notice">
            <strong>{{ t("articlePage.doiLabel") }}:</strong> {{ detail.article.doi }}
          </p>
          <p v-if="detail.article.issueNumber" class="article-page__notice">
            <strong>{{ t("articlePage.issueLabel") }}{{ detail.article.issueNumber }}</strong> ({{ detail.article.issueYear }})
          </p>
        </template>
        <p v-else class="article-page__notice">{{ t("articlePage.readonlyNotice") }}</p>

        <h3>{{ t("articlePage.statusHistory") }}</h3>
        <p><StatusBadge :status="(detail.article.status as any)" /></p>

        <dl class="article-page__summary">
          <dt>{{ t("articleForm.titleEn") }}</dt>
          <dd>{{ detail.article.titleEn }}</dd>
          <dt>{{ t("articleForm.abstractRu") }}</dt>
          <dd>{{ detail.article.abstractRu }}</dd>
          <dt>{{ t("articleForm.topic") }}</dt>
          <dd>{{ detail.article.topic }}</dd>
          <dt>{{ t("articleForm.authorsTitle") }}</dt>
          <dd>{{ detail.article.authors.map((a) => a.fullName).join(", ") }}</dd>
        </dl>

        <section v-if="reviewerComments.length" class="article-page__feedback">
          <h3>{{ t("reviewerFeedback.title") }}</h3>
          <ul>
            <li v-for="(comment, idx) in reviewerComments" :key="idx">{{ comment }}</li>
          </ul>
        </section>

        <ArticleRevisionForm
          v-if="detail.article.status === 'needs_revision'"
          :article-id="articleId"
          @uploaded="load"
        />
      </section>
    </template>
  </div>
</template>

<style scoped>
.article-page__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.article-page__notice {
  color: var(--color-text-secondary);
}

.article-page__notice--rejected {
  color: var(--color-error);
  font-weight: 600;
}

.article-page__notice--accepted {
  color: var(--color-success);
  font-weight: 600;
}

.article-page__summary {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--spacing-sm) var(--spacing-md);
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.article-page__summary dt {
  color: var(--color-text-secondary);
}

.article-page__summary dd {
  margin: 0;
}

.article-page__feedback {
  margin-bottom: var(--spacing-lg);
}

.article-page__feedback ul {
  padding-left: var(--spacing-lg);
}

.article-page__feedback li {
  margin-bottom: var(--spacing-sm);
}
</style>
