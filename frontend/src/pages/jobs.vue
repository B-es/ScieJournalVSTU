<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("jobsPage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("jobsPage.title") }}</h1>
        <br />

        <MarkdownContent
            v-if="t('jobsPage.text')"
            :content="t('jobsPage.text')"
        />
        <p v-else class="static-text-page__empty">{{ t("jobsPage.empty") }}</p>
    </div>
</template>

<style scoped>
.static-text-page__text {
    white-space: pre-wrap;
}

.static-text-page__empty {
    color: var(--color-text-secondary);
}
</style>
