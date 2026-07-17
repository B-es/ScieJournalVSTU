import { apiFetch } from "~/api/http";

/**
 * Notification type — mirrors `Notification.TYPE_CHOICES` from
 * `apps/notifications/models.py` (TS section 6, entity Notification).
 */
export type NotificationType =
  "status_changed" | "reviewer_invited" | "comment_added" | "decision_made";

/**
 * Shape of a single notification returned by GET /api/notifications.
 * Field names are camelCased per TS section 4 (frontend naming convention);
 * backend serialiser renames snake_case DB columns accordingly.
 */
export interface NotificationItem {
  id: string;
  type: NotificationType;
  message: string;
  isRead: boolean;
  articleId: string | null;
  createdAt: string;
}

/**
 * TS section 7, module "Уведомления": GET /api/notifications.
 * Optional filters mirror the query params handled by
 * `NotificationsListView.get` in `apps/notifications/views.py`.
 */
export function listNotifications(filters?: {
  isRead?: boolean;
  type?: NotificationType;
}) {
  const params = new URLSearchParams();
  if (filters?.isRead !== undefined)
    params.set("is_read", String(filters.isRead));
  if (filters?.type) params.set("type", filters.type);

  const query = params.toString() ? `?${params.toString()}` : "";
  // Trailing slash — same APPEND_SLASH convention as reviews.ts / articles.ts.
  return apiFetch<{ items: NotificationItem[] }>(`/notifications/${query}`);
}

/**
 * TS section 7, module "Уведомления": PATCH /api/notifications/{id}/read.
 * Marks a single notification as read. The backend is idempotent — calling
 * this on an already-read notification still returns { status: "ok" }.
 */
export function markNotificationRead(notificationId: string) {
  return apiFetch<{ status: string }>(`/notifications/${notificationId}/read`, {
    method: "PATCH",
  });
}
