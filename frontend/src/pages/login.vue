<script setup lang="ts">
import { ApiError } from "~/api/http";
import { useAuthStore } from "~/stores/auth";
import AppFormField from "~/components/AppFormField.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
const auth = useAuthStore();
const route = useRoute();

const email = ref("");
const password = ref("");
const fieldErrors = ref<Record<string, string>>({});
const formError = ref("");
const isSubmitting = ref(false);

function validate(): boolean {
  const errors: Record<string, string> = {};
  if (!email.value) errors.email = t("auth.validation.required");
  else if (!/^\S+@\S+\.\S+$/.test(email.value)) errors.email = t("auth.validation.email");
  if (!password.value) errors.password = t("auth.validation.required");
  fieldErrors.value = errors;
  return Object.keys(errors).length === 0;
}

async function handleSubmit() {
  formError.value = "";
  if (!validate()) return;

  isSubmitting.value = true;
  try {
    await auth.login(email.value, password.value);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/cabinet";
    await navigateTo(redirect);
  } catch (err) {
    formError.value = err instanceof ApiError ? t("auth.login.error") : t("common.error");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <h1>{{ t("auth.login.title") }}</h1>
    <br></br>
    <form class="auth-form" novalidate @submit.prevent="handleSubmit">
      <AppFormField
        v-model="email"
        :label="t('auth.login.email')"
        type="email"
        required
        autocomplete="email"
        :error="fieldErrors.email"
      />
      <AppFormField
        v-model="password"
        :label="t('auth.login.password')"
        type="password"
        required
        autocomplete="current-password"
        :error="fieldErrors.password"
      />

      <p v-if="formError" class="auth-form__error" role="alert" aria-live="assertive">{{ formError }}</p>

      <button type="submit" class="btn btn--primary" :disabled="isSubmitting" :aria-disabled="isSubmitting">
        {{ isSubmitting ? t("common.loading") : t("auth.login.submit") }}
      </button>
    </form>

    <p class="auth-page__hint">
      {{ t("auth.login.noAccount") }}
      <NuxtLink to="/register">{{ t("auth.login.registerLink") }}</NuxtLink>
    </p>
  </div>
</template>

<style scoped>
.auth-page {
  max-width: 420px;
  margin: 0 auto;
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.auth-form__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
  margin: 0 0 var(--spacing-md);
}

.btn--primary {
  height: 40px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
}

.btn--primary[aria-disabled="true"] {
  opacity: 0.4;
  cursor: not-allowed;
}

.auth-page__hint {
  margin-top: var(--spacing-lg);
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}
</style>
