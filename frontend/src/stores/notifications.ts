import { defineStore } from "pinia";
import {
  listNotifications,
  markNotificationRead,
  type NotificationItem,
} from "~/api/notifications";

/**
 * TS section 9: `notificationsStore` — unread counter shown in the cabinet
 * header, plus the underlying list used by the notifications dropdown/page.
 *
 * Backed by the real API from `~/api/notifications` (TS section 7, module
 * "Уведомления"). The store keeps the full list in memory so that toggling
 * the dropdown doesn't re-fetch; call `refresh()` explicitly when you need
 * to invalidate (e.g. after a status change that triggers new notifications).
 */
export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    items: [] as NotificationItem[],
    isLoading: false,
    /**
     * Last error caught during `refresh()`. Kept in state so the UI can
     * show an inline "failed to load notifications" banner instead of
     * silently hiding the bell.
     */
    loadError: null as string | null,
  }),

  getters: {
    /** TS section 9 — the number rendered as the badge in the cabinet header. */
    unreadCount(state): number {
      return state.items.filter((n) => !n.isRead).length;
    },
  },

  actions: {
    /**
     * Fetch the current user's notifications. Idempotent — safe to call on
     * every cabinet layout mount; the backend is a simple SELECT filtered
     * by `user=request.user`.
     */
    async refresh() {
      this.isLoading = true;
      this.loadError = null;
      try {
        const { items } = await listNotifications();
        this.items = items;
      } catch (err) {
        // Keep the previous list on transient network errors so the badge
        // doesn't flicker to zero; surface the error for the UI to render.
        this.loadError = err instanceof Error ? err.message : String(err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Mark a single notification as read. Uses optimistic update: the local
     * `isRead` flag flips immediately, then the PATCH is fired. The backend
     * is idempotent (PATCH on an already-read notification returns 200), so
     * a failed request simply leaves the item marked — the next `refresh()`
     * will reconcile.
     */
    async markRead(notificationId: string) {
      const target = this.items.find((n) => n.id === notificationId);
      if (!target || target.isRead) return;

      target.isRead = true;
      try {
        await markNotificationRead(notificationId);
      } catch {
        // Roll back so the badge count stays consistent with the server.
        target.isRead = false;
      }
    },

    /**
     * Called from `authStore.logout()` (or the cabinet layout's unmount
     * hook) to avoid leaking stale data into the next session.
     */
    reset() {
      this.items = [];
      this.isLoading = false;
      this.loadError = null;
    },
  },
});
