<script setup lang="ts">
import AppHeaderCabinet from "~/components/cabinet/AppHeaderCabinet.vue";
import CabinetSidebar from "~/components/cabinet/CabinetSidebar.vue";
import { onMounted } from "vue";
const notifications = useNotificationsStore();
onMounted(() => {
    notifications.refresh();
});
</script>

<template>
    <div class="layout-cabinet">
        <AppHeaderCabinet />
        <div class="layout-cabinet__body">
            <CabinetSidebar class="layout-cabinet__sidebar" />
            <main class="layout-cabinet__content">
                <slot />
            </main>
        </div>
    </div>
</template>

<style scoped>
.layout-cabinet {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.layout-cabinet__body {
    flex: 1;
    display: grid;
    /* DS section 3: 2/12 sidebar, 10/12 content */
    grid-template-columns: calc(
            var(--grid-cabinet-sidebar) / var(--grid-columns-desktop) * 100%
        ) 1fr;
    gap: var(--grid-gutter);
    max-width: var(--grid-container-width);
    margin: 0 auto;
    width: 100%;
    padding: var(--spacing-lg);
}

.layout-cabinet__sidebar {
    border-right: 1px solid var(--color-border);
    padding-right: var(--spacing-md);
}

.layout-cabinet__content {
    min-width: 0;
}

@media (max-width: 767px) {
    .layout-cabinet__body {
        grid-template-columns: 1fr;
    }

    .layout-cabinet__sidebar {
        display: none;
    }
}
</style>
