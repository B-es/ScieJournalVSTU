<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("editorsPage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("editorsPage.title") }}</h1>
        <br />

        <MarkdownContent
            v-if="t('editorsPage.text')"
            :content="t('editorsPage.text')"
        />
        <p v-else class="static-text-page__empty">
            {{ t("editorsPage.empty") }}
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
