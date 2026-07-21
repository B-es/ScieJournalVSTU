<script setup lang="ts">
import MarkdownContent from "~/components/public/MarkdownContent.vue";
import { getJournalSettings, type PublicJournalSettings } from "~/api/public";

definePageMeta({ layout: "public" });

const { t, locale } = useI18n();
useSeoMeta({ title: `${t("aboutPage.title")} — ${t("app.title")}` });

const settings = ref<PublicJournalSettings | null>(null);
const loading = ref(true);
const error = ref("");

async function load() {
    loading.value = true;
    error.value = "";
    try {
        settings.value = await getJournalSettings();
    } catch {
        error.value = t("common.error");
    } finally {
        loading.value = false;
    }
}

const board = computed(() =>
    [...(settings.value?.editorialBoard ?? [])].sort(
        (a, b) => a.order - b.order,
    ),
);

function memberName(m: (typeof board.value)[number]) {
    return locale.value === "en" ? m.fullNameEn : m.fullNameRu;
}
function memberRole(m: (typeof board.value)[number]) {
    return locale.value === "en" ? m.roleEn : m.roleRu;
}
function memberAffiliation(m: (typeof board.value)[number]) {
    return locale.value === "en" ? m.affiliationEn : m.affiliationRu;
}

onMounted(load);
</script>

<template>
    <div>
        <h1>{{ t("aboutPage.title") }}</h1>
        <br />

        <p v-if="loading">{{ t("common.loading") }}</p>
        <div v-else-if="error">
            <p>{{ error }}</p>
            <button type="button" class="btn btn--secondary" @click="load">
                {{ t("common.retry") }}
            </button>
        </div>
        <template v-else-if="settings">
            <p v-if="settings.issn" class="about-page__issn">
                ISSN: {{ settings.issn }}
            </p>

            <div v-if="t('aboutPage.text')" class="about-page__text">
                <MarkdownContent :content="t('aboutPage.text')" />
            </div>

            <section v-if="board.length" class="about-page__board">
                <h2>{{ t("aboutPage.editorialBoard") }}</h2>
                <ul class="about-page__board-list">
                    <li
                        v-for="(member, idx) in board"
                        :key="idx"
                        class="about-page__board-member"
                    >
                        <strong>{{ memberName(member) }}</strong>
                        <span v-if="memberRole(member)">
                            — {{ memberRole(member) }}</span
                        >
                        <div
                            v-if="memberAffiliation(member)"
                            class="about-page__board-affiliation"
                        >
                            {{ memberAffiliation(member) }}
                        </div>
                    </li>
                </ul>
            </section>
        </template>
    </div>
</template>

<style scoped>
.about-page__issn {
    color: var(--color-text-secondary);
}

.about-page__text {
    margin-bottom: var(--spacing-xl);
}

.about-page__board-list {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.about-page__board-member {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
}

.about-page__board-affiliation {
    color: var(--color-text-secondary);
    font-size: var(--type-caption-size);
}

.btn {
    display: inline-flex;
    align-items: center;
    height: 40px;
    padding: 0 var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: var(--type-button-size);
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--color-border);
    background: transparent;
    color: var(--color-text-primary);
}
</style>
