<script setup lang="ts">
definePageMeta({ layout: "public" });

const { t } = useI18n();
useHead({ title: t("app.title") });
</script>

<template>
  <div>
    <h1>{{ t("app.title") }}</h1>
    <p style="color: var(--color-text-secondary)">
      Главная страница со списком выпусков и статей появится в следующем milestone (US-10).
    </p>
  </div>
</template>
