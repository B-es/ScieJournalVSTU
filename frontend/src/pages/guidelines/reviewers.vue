<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("reviewersPage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("reviewersPage.title") }}</h1>
        <br />

        <MarkdownContent
            v-if="t('reviewersPage.text')"
            :content="t('reviewersPage.text')"
        />
        <p v-else class="static-text-page__empty">
            {{ t("reviewersPage.empty") }}
        </p>
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
