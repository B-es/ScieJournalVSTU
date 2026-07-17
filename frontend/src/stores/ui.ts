import { defineStore } from "pinia";

export interface Toast {
  id: number;
  type: "success" | "error" | "warning" | "info";
  message: string;
}

let nextToastId = 1;

/**
 * TS section 9: global loading/error flags for toasts.
 *
 * Note on language state: an earlier version of this store wrapped
 * `useI18n()` in a getter/action to expose `language`/`setLanguage`. That
 * broke at runtime ("Must be called at the top of a `setup` function") —
 * Pinia getters/actions run outside any component's setup call stack, and
 * useI18n() relies on Vue's inject(), which requires one. Composables like
 * useI18n() must be called directly inside a component's <script setup>
 * instead (see AppHeaderPublic.vue / AppHeaderCabinet.vue). i18n's own
 * `locale` ref is already the single source of truth for the current
 * language, so there's nothing left to duplicate here.
 */
export const useUiStore = defineStore("ui", {
  state: () => ({
    isLoading: false,
    toasts: [] as Toast[],
  }),

  actions: {
    pushToast(type: Toast["type"], message: string, timeoutMs = 4000) {
      const toast: Toast = { id: nextToastId++, type, message };
      this.toasts.push(toast);
      if (import.meta.client) {
        setTimeout(() => this.dismissToast(toast.id), timeoutMs);
      }
    },

    dismissToast(id: number) {
      this.toasts = this.toasts.filter((t) => t.id !== id);
    },
  },
});
