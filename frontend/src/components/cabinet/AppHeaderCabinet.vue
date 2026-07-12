<script setup lang="ts">
import { Bell } from "lucide-vue-next";
import { useAuthStore } from "~/stores/auth";
import { useNotificationsStore } from "~/stores/notifications";

const { t, locale, setLocale } = useI18n();
const auth = useAuthStore();
const notifications = useNotificationsStore();

async function handleLogout() {
  await auth.logout();
  await navigateTo("/login");
}
</script>

<template>
  <header class="header-cabinet">
    <div class="header-cabinet__inner">
      <NuxtLink to="/" class="header-cabinet__logo">{{ t("app.title") }}</NuxtLink>

      <div class="header-cabinet__actions">
        <NuxtLink to="/cabinet/notifications" class="icon-btn" :aria-label="t('cabinet.nav.notifications')">
          <Bell :size="20" />
          <span v-if="notifications.unreadCount > 0" class="icon-btn__badge">{{ notifications.unreadCount }}</span>
        </NuxtLink>

        <div class="lang-switch" role="group" aria-label="Язык">
          <button type="button" :class="{ active: locale === 'ru' }" @click="setLocale('ru')">RU</button>
          <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">EN</button>
        </div>

        <div class="avatar" :title="auth.user?.full_name">{{ (auth.user?.full_name ?? "?").charAt(0) }}</div>
        <button type="button" class="btn btn--secondary" @click="handleLogout">{{ t("nav.logout") }}</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-cabinet {
  border-bottom: 1px solid var(--color-border);
  background: var(--color-background);
}

.header-cabinet__inner {
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-cabinet__logo {
  font-size: var(--type-h3-size);
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
}

.header-cabinet__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.icon-btn {
  position: relative;
  display: inline-flex;
  color: var(--color-text-primary);
}

.icon-btn__badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background: var(--color-error);
  color: var(--color-text-inverse);
  font-size: 10px;
  line-height: 1;
  padding: 2px 5px;
  border-radius: 999px;
}

.lang-switch {
  display: flex;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
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

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  text-transform: uppercase;
}

.btn {
  height: 32px;
  display: inline-flex;
  align-items: center;
  padding: 0 var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--type-caption-size);
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-primary);
}
</style>
