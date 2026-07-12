<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

definePageMeta({ layout: "cabinet" });

const auth = useAuthStore();
</script>

<template>
  <div>
    <h2>Личный кабинет</h2>
    <p style="color: var(--color-text-secondary)">
      Добро пожаловать, {{ auth.user?.full_name }}. Экраны «Мои статьи», «Подать статью» и другие появятся в
      следующем milestone вместе с соответствующими API.
    </p>
  </div>
</template>
