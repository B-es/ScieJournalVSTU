<script setup lang="ts">
import {
    listPublicArticles,
    listPublicIssues,
    type PublicArticle,
    type PublicIssue,
} from "~/api/public";
import ArticleCard from "~/components/public/ArticleCard.vue";
import IssueCard from "~/components/public/IssueCard.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: t("app.title"), description: t("home.seoDescription") });

const latestIssue = ref<PublicIssue | null>(null);
const recentArticles = ref<PublicArticle[]>([]);
const loading = ref(true);
const error = ref("");

async function load() {
    loading.value = true;
    error.value = "";
    try {
        const [issues, articles] = await Promise.all([
            listPublicIssues(),
            listPublicArticles({ pageSize: 6 }),
        ]);
        latestIssue.value = issues.items[0] ?? null;
        recentArticles.value = articles.items;
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
        <p v-if="loading">{{ t("common.loading") }}</p>
        <div v-else-if="error">
            <p>{{ error }}</p>
            <button type="button" class="btn btn--secondary" @click="load">
                {{ t("common.retry") }}
            </button>
        </div>
        <template v-else>
            <section v-if="latestIssue" class="home-section">
                <h2>{{ t("home.latestIssue") }}</h2>
                <IssueCard :issue="latestIssue" />
            </section>

            <section class="home-section">
                <h2>{{ t("home.recentArticles") }}</h2>
                <p v-if="!recentArticles.length">{{ t("home.noArticles") }}</p>
                <div v-else class="home-articles-grid">
                    <ArticleCard
                        v-for="article in recentArticles"
                        :key="article.id"
                        :article="article"
                    />
                </div>
            </section>
        </template>
    </div>
</template>

<style scoped>
.home-section {
    margin-bottom: var(--spacing-xl);
}

.home-articles-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md);
}

@media (max-width: 1279px) {
    .home-articles-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 767px) {
    .home-articles-grid {
        grid-template-columns: 1fr;
    }
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
    border: 1px solid var(--color-border);
    background: transparent;
    color: var(--color-text-primary);
}
</style>
