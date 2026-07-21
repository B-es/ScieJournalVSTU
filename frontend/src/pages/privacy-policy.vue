<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
useSeoMeta({ title: `${t("privacyPolicyPage.title")} — ${t("app.title")}` });
</script>

<template>
    <div class="static-text-page">
        <h1>{{ t("privacyPolicyPage.title") }}</h1>

        <MarkdownContent
            v-if="t('privacyPolicyPage.text')"
            :content="t('privacyPolicyPage.text')"
        />
        <p v-else class="static-text-page__empty">
            {{ t("privacyPolicyPage.empty") }}
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
