import { defineStore } from "pinia";

/**
 * Unread-notifications counter shown in the cabinet header (TS section 9).
 * Backed by a real API once the notifications module lands (see plan M3+);
 * for now it's a static placeholder so the header badge has something to
 * bind to.
 */
export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    unreadCount: 0,
  }),
});
