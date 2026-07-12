<script setup lang="ts">
import { CheckCircle2, Clock, Edit3, Eye, RotateCcw, XCircle } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{
  status: "draft" | "submitted" | "needs_revision" | "rejected" | "in_review" | "accepted" | "published";
}>();

const { t } = useI18n();

const ICONS = {
  draft: Edit3,
  submitted: Clock,
  needs_revision: RotateCcw,
  rejected: XCircle,
  in_review: Eye,
  accepted: CheckCircle2,
  published: CheckCircle2,
};

const icon = computed(() => ICONS[props.status]);
const label = computed(() => t(`articleStatus.${props.status}`));
</script>

<template>
  <span class="status-badge" :class="`status-badge--${status}`">
    <component :is="icon" :size="14" aria-hidden="true" />
    {{ label }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  height: 24px;
  padding: 0 var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--type-caption-size);
  font-weight: 500;
  color: var(--color-text-inverse);
  white-space: nowrap;
}

.status-badge--draft {
  background: var(--color-status-draft);
}
.status-badge--submitted {
  background: var(--color-status-submitted);
}
.status-badge--needs_revision {
  background: var(--color-status-revision);
  color: var(--color-text-primary);
}
.status-badge--rejected {
  background: var(--color-status-rejected);
}
.status-badge--in_review {
  background: var(--color-status-in-review);
}
.status-badge--accepted {
  background: var(--color-status-accepted);
}
.status-badge--published {
  background: var(--color-status-published);
}
</style>
