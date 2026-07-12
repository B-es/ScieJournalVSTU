<script setup lang="ts">
const { t } = useI18n();

const links = computed(() => [
  { to: "/open-access-policy", label: t("footer.openAccessPolicy") },
  { to: "/jobs", label: t("footer.jobs") },
  { to: "/guidelines/authors", label: t("footer.guidelinesForAuthors") },
  { to: "/guidelines/reviewers", label: t("footer.guidelinesForReviewers") },
  { to: "/guidelines/editors", label: t("footer.guidelinesForEditors") },
  { to: "/terms-of-use", label: t("footer.termsOfUse") },
  { to: "/privacy-policy", label: t("footer.privacyPolicy") },
  { to: "/terms-and-conditions", label: t("footer.termsAndConditions") },
  { to: "/help", label: t("footer.help") },
]);

const year = new Date().getFullYear();
</script>

<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <nav class="app-footer__links" aria-label="Вспомогательные страницы">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to">{{ link.label }}</NuxtLink>
      </nav>
      <p class="app-footer__copyright">© {{ year }} {{ t("app.title") }}</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  margin-top: var(--spacing-xl);
}

.app-footer__inner {
  max-width: var(--grid-container-width);
  margin: 0 auto;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.app-footer__links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.app-footer__links a {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--type-caption-size);
}

.app-footer__copyright {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
}
</style>
