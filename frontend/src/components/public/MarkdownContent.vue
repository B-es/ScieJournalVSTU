<script setup lang="ts">
const props = defineProps<{ content: string }>();

function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[m] || m));
}

function renderMarkdown(text: string): string {
  if (!text) return '';

  const lines = text.split('\n');
  let html = '';
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Skip empty lines but close any open list
    if (line.trim() === '') {
      if (inList) { html += '</ul>'; inList = false; }
      continue;
    }

    // Headings ### -> h3, ## -> h2, # -> h1
    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      if (inList) { html += '</ul>'; inList = false; }
      const level = headingMatch[1].length;
      const title = inlineFormat(escapeHtml(headingMatch[2]));
      html += `<h${level}>${title}</h${level}>`;
      continue;
    }

    // Unordered list items (- text)
    const listMatch = line.match(/^[-*]\s+(.+)$/);
    if (listMatch) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${inlineFormat(escapeHtml(listMatch[1]))}</li>`;
      continue;
    }

    // Ordered list items (1. text, 2. etc.)
    const orderedMatch = line.match(/^\d+\.\s+(.+)$/);
    if (orderedMatch) {
      if (inList) { html += '</ul>'; inList = false; }
      html += `<p class="static-text-page__ordered">${inlineFormat(escapeHtml(orderedMatch[1]))}</p>`;
      continue;
    }

    // Regular paragraph
    if (inList) { html += '</ul>'; inList = false; }
    html += `<p>${inlineFormat(escapeHtml(line))}</p>`;
  }

  if (inList) html += '</ul>';

  return html;
}

function inlineFormat(text: string): string {
  // Bold **text**
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic *text*
  text = text.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  return text;
}
</script>

<template>
  <div class="markdown-content" v-html="renderMarkdown(props.content)" />
</template>

<style scoped>
.markdown-content {
  white-space: normal;
  line-height: 1.6;
}

.markdown-content :deep(p) {
  margin: 0 0 var(--spacing-md);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
}

.markdown-content :deep(ul) {
  padding-left: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

.markdown-content :deep(li) {
  margin-bottom: var(--spacing-xs);
}

.markdown-content :deep(strong) {
  font-weight: 600;
}
</style>
