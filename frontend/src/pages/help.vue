<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("helpPage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("helpPage.title") }}</h1>

        <MarkdownContent
            v-if="t('helpPage.text')"
            :content="t('helpPage.text')"
        />
        <p v-else class="static-text-page__empty">{{ t("helpPage.empty") }}</p>
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
