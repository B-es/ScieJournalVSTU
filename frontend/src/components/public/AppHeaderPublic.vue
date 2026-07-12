<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const { t, locale, setLocale } = useI18n();
const auth = useAuthStore();

const navLinks = computed(() => [
  { to: "/", label: t("nav.home") },
  { to: "/about", label: t("nav.about") },
  { to: "/archive", label: t("nav.archive") },
  { to: "/for-authors", label: t("nav.forAuthors") },
  { to: "/search", label: t("nav.search") },
]);

async function handleLogout() {
  await auth.logout();
  await navigateTo("/");
}
</script>

<template>
  <header class="header-public">
    <div class="header-public__inner">
      <NuxtLink to="/" class="header-public__logo">{{ t("app.title") }}</NuxtLink>

      <nav class="header-public__nav" aria-label="Главное меню">
        <NuxtLink v-for="link in navLinks" :key="link.to" :to="link.to">{{ link.label }}</NuxtLink>
      </nav>

      <div class="header-public__actions">
        <div class="lang-switch" role="group" aria-label="Язык">
          <button type="button" :class="{ active: locale === 'ru' }" @click="setLocale('ru')">RU</button>
          <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">EN</button>
        </div>

        <template v-if="auth.isAuthenticated">
          <NuxtLink to="/cabinet" class="btn btn--secondary">{{ auth.user?.full_name }}</NuxtLink>
          <button type="button" class="btn btn--secondary" @click="handleLogout">{{ t("nav.logout") }}</button>
        </template>
        <template v-else>
          <NuxtLink to="/login" class="btn btn--secondary">{{ t("nav.login") }}</NuxtLink>
          <NuxtLink to="/register" class="btn btn--primary">{{ t("nav.register") }}</NuxtLink>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-public {
  border-bottom: 1px solid var(--color-border);
  background: var(--color-background);
}

.header-public__inner {
  max-width: var(--grid-container-width);
  margin: 0 auto;
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.header-public__logo {
  font-family: var(--font-family-base);
  font-size: var(--type-h3-size);
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
  white-space: nowrap;
}

.header-public__nav {
  display: flex;
  gap: var(--spacing-lg);
  flex: 1;
}

.header-public__nav a {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--type-body-size);
}

.header-public__nav a.router-link-active {
  color: var(--color-primary);
}

.header-public__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.lang-switch {
  display: flex;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-right: var(--spacing-sm);
}

.lang-switch button {
  border: none;
  background: transparent;
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--type-caption-size);
  cursor: pointer;
  color: var(--color-text-secondary);
}

.lang-switch button.active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

@media (max-width: 767px) {
  .header-public__nav {
    display: none;
  }
}
</style>
