<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({
    title: `${t("termsAndConditionsPage.title")} — ${t("app.title")}`,
});
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("termsAndConditionsPage.title") }}</h1>

        <MarkdownContent
            v-if="t('termsAndConditionsPage.text')"
            :content="t('termsAndConditionsPage.text')"
        />
        <p v-else class="static-text-page__empty">
            {{ t("termsAndConditionsPage.empty") }}
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
