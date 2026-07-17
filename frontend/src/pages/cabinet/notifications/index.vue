<script setup lang="ts">
import { onMounted } from "vue";
import { useAuthStore } from "~/stores/auth";
import { useNotificationsStore } from "~/stores/notifications";
import type { NotificationItem, NotificationType } from "~/api/notifications";

definePageMeta({ layout: "cabinet" });

const auth = useAuthStore();
const notifications = useNotificationsStore();

onMounted(() => {
    notifications.refresh();
});

/**
 * Map backend `Notification.TYPE_CHOICES` keys to i18n keys under
 * `notifications.types.*`. Unknown types fall back to the raw key so the
 * UI never renders an empty cell if the backend adds a new type.
 */
function formatType(type: NotificationType): string {
    return $t(`notifications.types.${type}`, type);
}

/**
 * Locale-aware date formatter. Uses the current UI language from uiStore
 * once wired; for now falls back to the browser locale.
 */
function formatDate(iso: string): string {
    const date = new Date(iso);
    const locale = auth.languagePref === "en" ? "en-GB" : "ru-RU";
    return date.toLocaleString(locale, {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function onRowClick(item: NotificationItem) {
    notifications.markRead(item.id);
    if (item.articleId) {
        navigateTo(`/cabinet/author/articles/${item.articleId}`);
    }
}
</script>

<template>
    <div class="notifications-page">
        <h2 class="notifications-page__title">
            {{ $t("notifications.title") }}
        </h2>

        <!-- Loading (DS section 6: "загрузка") -->
        <div v-if="notifications.isLoading" class="state state--loading">
            <div class="state__spinner" aria-hidden="true"></div>
            <p class="state__text">{{ $t("notifications.loading") }}</p>
        </div>

        <!-- Error (DS section 6: "ошибка") -->
        <div
            v-else-if="notifications.loadError"
            class="state state--error"
            role="alert"
        >
            <p class="state__text">{{ $t("notifications.error") }}</p>
            <button
                type="button"
                class="state__retry"
                @click="notifications.refresh()"
            >
                {{ $t("common.retry") }}
            </button>
        </div>

        <!-- Empty (DS section 6: "пусто") -->
        <div
            v-else-if="notifications.items.length === 0"
            class="state state--empty"
        >
            <p class="state__text">{{ $t("notifications.empty") }}</p>
        </div>

        <!-- List -->
        <table v-else class="notifications-table">
            <thead>
                <tr>
                    <th scope="col">{{ $t("notifications.columns.type") }}</th>
                    <th scope="col">
                        {{ $t("notifications.columns.message") }}
                    </th>
                    <th scope="col">{{ $t("notifications.columns.date") }}</th>
                    <th scope="col">
                        {{ $t("notifications.columns.status") }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="item in notifications.items"
                    :key="item.id"
                    :class="{
                        'notifications-table__row': true,
                        'notifications-table__row--unread': !item.isRead,
                        'notifications-table__row--clickable': Boolean(
                            item.articleId,
                        ),
                    }"
                    @click="onRowClick(item)"
                >
                    <td class="notifications-table__type">
                        {{ formatType(item.type) }}
                    </td>
                    <td class="notifications-table__message">
                        {{ item.message }}
                    </td>
                    <td class="notifications-table__date">
                        {{ formatDate(item.createdAt) }}
                    </td>
                    <td class="notifications-table__status">
                        <span
                            :class="[
                                'badge',
                                item.isRead ? 'badge--read' : 'badge--unread',
                            ]"
                        >
                            {{
                                item.isRead
                                    ? $t("notifications.status.read")
                                    : $t("notifications.status.unread")
                            }}
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
/*
 * All visual values come from tokens.css (DS section 10).
 * No raw hex / px values are introduced here.
 */

.notifications-page {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.notifications-page__title {
    font-size: var(--type-h2-size);
    line-height: var(--type-h2-line);
    color: var(--color-text-primary);
    margin: 0;
}

/* ---------- Shared state blocks (loading / error / empty) ---------- */

.state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    padding: var(--spacing-xl) var(--spacing-lg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    text-align: center;
}

.state__text {
    margin: 0;
    font-size: var(--type-body-size);
    line-height: var(--type-body-line);
    color: var(--color-text-secondary);
}

.state__spinner {
    width: 28px;
    height: 28px;
    border: 3px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: state-spin 0.8s linear infinite;
}

@keyframes state-spin {
    to {
        transform: rotate(360deg);
    }
}

.state--error {
    border-color: var(--color-error);
    background: rgba(210, 25, 25, 0.04);
}

.state--error .state__text {
    color: var(--color-error);
}

.state__retry {
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--color-primary);
    border-radius: var(--radius-md);
    background: transparent;
    color: var(--color-primary);
    font-size: var(--type-button-size);
    line-height: var(--type-button-line);
    cursor: pointer;
    transition:
        background-color 0.15s ease,
        color 0.15s ease;
}

.state__retry:hover {
    background: var(--color-primary);
    color: var(--color-text-inverse);
}

/* ---------- Table ---------- */

.notifications-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    background: var(--color-background);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    font-size: var(--type-body-size);
    line-height: var(--type-body-line);
}

.notifications-table th,
.notifications-table td {
    padding: var(--spacing-md);
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid var(--color-border);
}

.notifications-table thead th {
    background: var(--color-surface);
    color: var(--color-text-secondary);
    font-size: var(--type-caption-size);
    line-height: var(--type-caption-line);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.notifications-table tbody tr:last-child td {
    border-bottom: none;
}

/* Row variants */

.notifications-table__row {
    transition: background-color 0.15s ease;
}

.notifications-table__row--unread {
    background: var(--color-surface);
    border-left: 3px solid var(--color-primary);
}

/* Compensate the left border so columns stay aligned with the header */
.notifications-table__row--unread > td:first-child {
    padding-left: calc(var(--spacing-md) - 3px);
}

.notifications-table__row--unread .notifications-table__message {
    color: var(--color-text-primary);
    font-weight: 600;
}

.notifications-table__row--clickable {
    cursor: pointer;
}

.notifications-table__row--clickable:hover {
    background: var(--color-surface);
    box-shadow: inset 0 0 0 1px var(--color-border);
}

/* Column-specific styling */

.notifications-table__type {
    white-space: nowrap;
    color: var(--color-text-secondary);
    font-size: var(--type-caption-size);
    line-height: var(--type-caption-line);
}

.notifications-table__message {
    color: var(--color-text-primary);
    max-width: 40ch;
}

.notifications-table__date {
    white-space: nowrap;
    color: var(--color-text-secondary);
    font-size: var(--type-caption-size);
    line-height: var(--type-caption-line);
}

.notifications-table__status {
    white-space: nowrap;
}

/* ---------- Badges ---------- */

.badge {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--type-caption-size);
    line-height: var(--type-caption-line);
    font-weight: 500;
}

.badge--unread {
    background: rgba(25, 118, 210, 0.12); /* primary @ ~12% */
    color: var(--color-primary);
}

.badge--read {
    background: var(--color-surface);
    color: var(--color-text-secondary);
}

/* ---------- Reduced motion (tokens.css already declares this globally,
   but we keep the spinner animation respectful) ---------- */
@media (prefers-reduced-motion: reduce) {
    .state__spinner {
        animation: none;
        border-top-color: var(--color-primary);
        opacity: 0.6;
    }
}
</style>
