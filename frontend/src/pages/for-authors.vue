<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";
import { getJournalSettings } from "~/api/public";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("forAuthorsPage.title")} — ${t("app.title")}` });

const loading = ref(true);
const error = ref("");

async function load() {
    loading.value = true;
    error.value = "";
    try {
        await getJournalSettings();
    } catch {
        // settings endpoint is used only to keep editorialBoard data flowing if needed later
        error.value = "";
    } finally {
        loading.value = false;
    }
}

onMounted(load);
</script>

<template>
    <div>
        <h1>{{ t("forAuthorsPage.title") }}</h1>

        <p v-if="loading">{{ t("common.loading") }}</p>
        <div v-else-if="error">
            <p>{{ error }}</p>
            <button type="button" class="btn btn--secondary" @click="load">
                {{ t("common.retry") }}
            </button>
        </div>

        <div v-else class="for-authors-page__text">
            <MarkdownContent
                v-if="t('forAuthorsPage.text')"
                :content="t('forAuthorsPage.text')"
            />
            <p v-else class="for-authors-page__empty">
                {{ t("forAuthorsPage.empty") }}
            </p>
        </div>
    </div>
</template>

<style scoped>
.for-authors-page__text {
    margin-bottom: var(--spacing-xl);
}

.for-authors-page__empty {
    color: var(--color-text-secondary);
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
