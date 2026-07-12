<script setup lang="ts">
import AppFooter from "~/components/public/AppFooter.vue";
import AppHeaderPublic from "~/components/public/AppHeaderPublic.vue";
</script>

<template>
  <div class="layout-public">
    <AppHeaderPublic />
    <main class="layout-public__content">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<style scoped>
.layout-public {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-public__content {
  flex: 1;
  width: 100%;
  max-width: var(--grid-container-width);
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
}

@media (max-width: 767px) {
  .layout-public__content {
    padding: var(--spacing-lg) var(--spacing-md);
  }
}
</style>
