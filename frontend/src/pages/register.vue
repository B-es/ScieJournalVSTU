<script setup lang="ts">
import { ApiError } from "~/api/http";
import { useAuthStore } from "~/stores/auth";
import AppFormField from "~/components/AppFormField.vue";

definePageMeta({ layout: "public" });

const { t } = useI18n();
const auth = useAuthStore();

const fullName = ref("");
const email = ref("");
const password = ref("");
const fieldErrors = ref<Record<string, string>>({});
const formError = ref("");
const isSubmitting = ref(false);

function validate(): boolean {
  const errors: Record<string, string> = {};
  if (!fullName.value) errors.fullName = t("auth.validation.required");
  if (!email.value) errors.email = t("auth.validation.required");
  else if (!/^\S+@\S+\.\S+$/.test(email.value)) errors.email = t("auth.validation.email");
  if (!password.value) errors.password = t("auth.validation.required");
  else if (password.value.length < 8) errors.password = t("auth.validation.minLength", { min: 8 });
  fieldErrors.value = errors;
  return Object.keys(errors).length === 0;
}

async function handleSubmit() {
  formError.value = "";
  if (!validate()) return;

  isSubmitting.value = true;
  try {
    await auth.register(fullName.value, email.value, password.value);
    await navigateTo("/cabinet");
  } catch (err) {
    if (err instanceof ApiError && err.status === 400) {
      formError.value = t("auth.register.emailTaken");
    } else {
      formError.value = t("auth.register.error");
    }
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <h1>{{ t("auth.register.title") }}</h1>
    <br></br>
    <form class="auth-form" novalidate @submit.prevent="handleSubmit">
      <AppFormField v-model="fullName" :label="t('auth.register.fullName')" required autocomplete="name" :error="fieldErrors.fullName" />
      <AppFormField
        v-model="email"
        :label="t('auth.register.email')"
        type="email"
        required
        autocomplete="email"
        :error="fieldErrors.email"
      />
      <AppFormField
        v-model="password"
        :label="t('auth.register.password')"
        type="password"
        required
        autocomplete="new-password"
        :error="fieldErrors.password"
      />

      <p v-if="formError" class="auth-form__error" role="alert" aria-live="assertive">{{ formError }}</p>

      <button type="submit" class="btn btn--primary" :disabled="isSubmitting" :aria-disabled="isSubmitting">
        {{ isSubmitting ? t("common.loading") : t("auth.register.submit") }}
      </button>
    </form>

    <p class="auth-page__hint">
      {{ t("auth.register.haveAccount") }}
      <NuxtLink to="/login">{{ t("auth.register.loginLink") }}</NuxtLink>
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
