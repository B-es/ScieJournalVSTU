<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("termsOfUsePage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("termsOfUsePage.title") }}</h1>

        <MarkdownContent
            v-if="t('termsOfUsePage.text')"
            :content="t('termsOfUsePage.text')"
        />
        <p v-else class="static-text-page__empty">
            {{ t("termsOfUsePage.empty") }}
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
