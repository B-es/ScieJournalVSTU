<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const { t } = useI18n();
const auth = useAuthStore();

interface SidebarLink {
  to: string;
  label: string;
}

// DS section 5 (site map): menu contents depend on the user's role(s). The
// technical editor has no dedicated cabinet (managed via Django Admin, see
// DS/TS notes) so it has no entry here.
const roleLinks = computed<SidebarLink[]>(() => {
  const links: SidebarLink[] = [];

  if (auth.hasRole("author")) {
    links.push(
      { to: "/cabinet/author/articles", label: t("cabinet.nav.myArticles") },
      { to: "/cabinet/author/submit", label: t("cabinet.nav.submitArticle") },
    );
  }
  if (auth.hasRole("reviewer")) {
    links.push(
      { to: "/cabinet/reviewer/articles", label: t("cabinet.nav.reviewArticles") },
      { to: "/cabinet/reviewer/invitations", label: t("cabinet.nav.invitations") },
    );
  }
  if (auth.hasRole("chief_editor")) {
    links.push(
      { to: "/cabinet/chief-editor/articles", label: t("cabinet.nav.manageArticles") },
      { to: "/cabinet/chief-editor/invitations", label: t("cabinet.nav.invitations") },
      { to: "/cabinet/chief-editor/decisions", label: t("cabinet.nav.decisions") },
    );
  }

  return links;
});

const commonLinks = computed<SidebarLink[]>(() => [
  { to: "/cabinet/notifications", label: t("cabinet.nav.notifications") },
  { to: "/cabinet/settings", label: t("cabinet.nav.settings") },
]);
</script>

<template>
  <aside class="cabinet-sidebar" aria-label="Меню личного кабинета">
    <nav class="cabinet-sidebar__nav">
      <NuxtLink v-for="link in roleLinks" :key="link.to" :to="link.to" class="cabinet-sidebar__link">
        {{ link.label }}
      </NuxtLink>
      <hr v-if="roleLinks.length" class="cabinet-sidebar__divider" >
      <NuxtLink v-for="link in commonLinks" :key="link.to" :to="link.to" class="cabinet-sidebar__link">
        {{ link.label }}
      </NuxtLink>
    </nav>
  </aside>
</template>

<style scoped>
.cabinet-sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.cabinet-sidebar__link {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: var(--type-body-size);
}

.cabinet-sidebar__link.router-link-active {
  background: var(--color-surface);
  color: var(--color-primary);
  font-weight: 500;
}

.cabinet-sidebar__divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-sm) 0;
}
</style>
