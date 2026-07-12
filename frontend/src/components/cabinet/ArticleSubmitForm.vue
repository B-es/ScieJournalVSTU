<script setup lang="ts">
import { onMounted, reactive, ref, watch } from "vue";
import * as articlesApi from "~/api/articles";
import { ApiError } from "~/api/http";
import AppFormField from "~/components/AppFormField.vue";
import AppFileField from "~/components/cabinet/AppFileField.vue";
import { debounce } from "~/utils/debounce";

const props = defineProps<{ articleId?: string }>();
const emit = defineEmits<{ submitted: [articleId: string] }>();

const { t } = useI18n();

const STEP_KEYS = ["metadata", "files", "review"] as const;
const currentStep = ref(0);

const articleId = ref<string | null>(props.articleId ?? null);
const isHydrating = ref(!!props.articleId);
const loadError = ref("");

const fields = reactive({
  titleRu: "",
  titleEn: "",
  abstractRu: "",
  abstractEn: "",
  keywordsRu: "",
  keywordsEn: "",
  topic: "",
});

interface AuthorRow {
  fullName: string;
  affiliation: string;
  email: string;
}

const authors = ref<AuthorRow[]>([{ fullName: "", affiliation: "", email: "" }]);

const manuscriptFile = ref<File | null>(null);
const existingManuscriptUrl = ref<string | null>(null);

interface DocumentRow {
  file: File;
  docType: string;
}

const newDocuments = ref<DocumentRow[]>([]);
const existingDocuments = ref<articlesApi.ArticleDocument[]>([]);

const saveState = ref<"idle" | "saving" | "saved" | "error">("idle");
const isSubmitting = ref(false);
const fieldErrors = ref<Record<string, string>>({});
const formError = ref("");

function splitKeywords(raw: string): string[] {
  return raw
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);
}

function currentPayload(): articlesApi.ArticleDraftPayload {
  return {
    articleId: articleId.value ?? undefined,
    titleRu: fields.titleRu,
    titleEn: fields.titleEn,
    abstractRu: fields.abstractRu,
    abstractEn: fields.abstractEn,
    keywordsRu: splitKeywords(fields.keywordsRu),
    keywordsEn: splitKeywords(fields.keywordsEn),
    topic: fields.topic,
    authors: authors.value.filter((a) => a.fullName.trim()),
  };
}

async function persistDraft(extra: Partial<articlesApi.ArticleDraftPayload> = {}) {
  saveState.value = "saving";
  try {
    const res = await articlesApi.saveDraft({ ...currentPayload(), ...extra });
    articleId.value = res.articleId;
    saveState.value = "saved";
  } catch {
    saveState.value = "error";
  }
}

const debouncedSave = debounce(() => {
  if (!isHydrating.value) persistDraft();
}, 1200);

watch(
  [fields, authors],
  () => {
    if (isHydrating.value) return;
    debouncedSave();
  },
  { deep: true },
);

async function handleManuscriptChange(file: File | null) {
  manuscriptFile.value = file;
  if (file) await persistDraft({ manuscriptFile: file });
}

function addDocumentSlot(file: File | null) {
  if (!file) return;
  newDocuments.value.push({ file, docType: "" });
}

async function saveNewDocuments() {
  if (!newDocuments.value.length) return;
  await persistDraft({ documents: newDocuments.value });
  newDocuments.value = [];
}

function addAuthorRow() {
  authors.value.push({ fullName: "", affiliation: "", email: "" });
}

function removeAuthorRow(index: number) {
  authors.value.splice(index, 1);
}

function goNext() {
  if (currentStep.value < STEP_KEYS.length - 1) currentStep.value += 1;
}

function goBack() {
  if (currentStep.value > 0) currentStep.value -= 1;
}

async function handleFinalSubmit() {
  formError.value = "";
  fieldErrors.value = {};

  if (!articleId.value) {
    await persistDraft();
  }
  if (!articleId.value) {
    formError.value = t("articleForm.submitError");
    return;
  }

  isSubmitting.value = true;
  try {
    const res = await articlesApi.submitArticle(articleId.value, currentPayload());
    emit("submitted", res.articleId);
  } catch (err) {
    if (err instanceof ApiError && err.fieldErrors) {
      const flat: Record<string, string> = {};
      for (const [field, msgs] of Object.entries(err.fieldErrors)) flat[field] = msgs[0];
      fieldErrors.value = flat;
    }
    formError.value = t("articleForm.submitError");
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(async () => {
  if (!props.articleId) return;
  try {
    const { article, versions } = await articlesApi.getArticle(props.articleId);
    fields.titleRu = article.titleRu;
    fields.titleEn = article.titleEn;
    fields.abstractRu = article.abstractRu;
    fields.abstractEn = article.abstractEn;
    fields.keywordsRu = article.keywordsRu.join(", ");
    fields.keywordsEn = article.keywordsEn.join(", ");
    fields.topic = article.topic;
    if (article.authors.length) {
      authors.value = article.authors.map((a) => ({
        fullName: a.fullName,
        affiliation: a.affiliation,
        email: a.email,
      }));
    }
    const version = versions.find((v) => v.versionNumber === 1);
    if (version) {
      existingManuscriptUrl.value = version.manuscriptFileUrl;
      existingDocuments.value = version.documents;
    }
  } catch {
    loadError.value = t("common.error");
  } finally {
    isHydrating.value = false;
  }
});
</script>

<template>
  <div class="article-form">
    <div class="article-form__steps" role="tablist">
      <span
        v-for="(key, index) in STEP_KEYS"
        :key="key"
        class="article-form__step"
        :class="{ 'article-form__step--active': currentStep === index }"
      >
        {{ index + 1 }}. {{ t(`articleForm.steps.${key}`) }}
      </span>
    </div>

    <p v-if="loadError" class="article-form__error" role="alert">{{ loadError }}</p>

    <!-- Step 1: metadata -->
    <section v-if="currentStep === 0">
      <AppFormField v-model="fields.titleRu" :label="t('articleForm.titleRu')" required />
      <AppFormField v-model="fields.titleEn" :label="t('articleForm.titleEn')" required />
      <AppFormField v-model="fields.abstractRu" :label="t('articleForm.abstractRu')" required />
      <AppFormField v-model="fields.abstractEn" :label="t('articleForm.abstractEn')" required />
      <AppFormField v-model="fields.keywordsRu" :label="t('articleForm.keywordsRu')" required />
      <AppFormField v-model="fields.keywordsEn" :label="t('articleForm.keywordsEn')" required />
      <AppFormField v-model="fields.topic" :label="t('articleForm.topic')" required />

      <h3>{{ t("articleForm.authorsTitle") }}</h3>
      <div v-for="(author, index) in authors" :key="index" class="article-form__author-row">
        <AppFormField v-model="author.fullName" :label="t('articleForm.authorFullName')" required />
        <AppFormField v-model="author.affiliation" :label="t('articleForm.authorAffiliation')" />
        <AppFormField v-model="author.email" :label="t('articleForm.authorEmail')" type="email" />
        <button
          v-if="authors.length > 1"
          type="button"
          class="btn btn--secondary"
          @click="removeAuthorRow(index)"
        >
          {{ t("articleForm.removeAuthor") }}
        </button>
      </div>
      <button type="button" class="btn btn--secondary" @click="addAuthorRow">
        {{ t("articleForm.addAuthor") }}
      </button>
    </section>

    <!-- Step 2: files -->
    <section v-if="currentStep === 1">
      <p v-if="existingManuscriptUrl" class="article-form__hint">
        <a :href="existingManuscriptUrl" target="_blank" rel="noopener">{{ existingManuscriptUrl.split("/").pop() }}</a>
      </p>
      <AppFileField
        :model-value="manuscriptFile"
        :label="t('articleForm.manuscriptFile')"
        accept=".doc,.docx,.pdf"
        required
        :error="fieldErrors.manuscriptFile"
        @update:model-value="handleManuscriptChange"
      />

      <h3>{{ t("articleForm.documentsTitle") }}</h3>
      <ul v-if="existingDocuments.length">
        <li v-for="doc in existingDocuments" :key="doc.id">
          <a :href="doc.fileUrl" target="_blank" rel="noopener">{{ doc.docType || doc.fileUrl.split("/").pop() }}</a>
        </li>
      </ul>
      <div v-for="(doc, index) in newDocuments" :key="index" class="article-form__author-row">
        <span>{{ doc.file.name }}</span>
        <AppFormField v-model="doc.docType" :label="t('articleForm.documentType')" />
      </div>
      <AppFileField :model-value="null" :label="t('articleForm.addDocument')" @update:model-value="addDocumentSlot" />
      <button v-if="newDocuments.length" type="button" class="btn btn--secondary" @click="saveNewDocuments">
        {{ t("articleForm.addDocument") }}
      </button>
    </section>

    <!-- Step 3: review -->
    <section v-if="currentStep === 2">
      <p class="article-form__hint">{{ t("articleForm.reviewHint") }}</p>
      <dl class="article-form__summary">
        <dt>{{ t("articleForm.titleRu") }}</dt>
        <dd>{{ fields.titleRu || "—" }}</dd>
        <dt>{{ t("articleForm.titleEn") }}</dt>
        <dd>{{ fields.titleEn || "—" }}</dd>
        <dt>{{ t("articleForm.topic") }}</dt>
        <dd>{{ fields.topic || "—" }}</dd>
        <dt>{{ t("articleForm.authorsTitle") }}</dt>
        <dd>{{ authors.map((a) => a.fullName).filter(Boolean).join(", ") || "—" }}</dd>
        <dt>{{ t("articleForm.manuscriptFile") }}</dt>
        <dd>{{ manuscriptFile?.name ?? existingManuscriptUrl?.split("/").pop() ?? "—" }}</dd>
      </dl>

      <p v-if="formError" class="article-form__error" role="alert" aria-live="assertive">{{ formError }}</p>
    </section>

    <footer class="article-form__footer">
      <span class="article-form__save-state">
        <template v-if="saveState === 'saving'">{{ t("articleForm.saving") }}</template>
        <template v-else-if="saveState === 'saved'">{{ t("articleForm.savedDraft") }}</template>
      </span>

      <div class="article-form__nav">
        <button v-if="currentStep > 0" type="button" class="btn btn--secondary" @click="goBack">
          {{ t("articleForm.back") }}
        </button>
        <button v-if="currentStep < STEP_KEYS.length - 1" type="button" class="btn btn--primary" @click="goNext">
          {{ t("articleForm.next") }}
        </button>
        <button
          v-else
          type="button"
          class="btn btn--primary"
          :disabled="isSubmitting"
          :aria-disabled="isSubmitting"
          @click="handleFinalSubmit"
        >
          {{ isSubmitting ? t("common.loading") : t("articleForm.submit") }}
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.article-form__steps {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.article-form__step {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
}

.article-form__step--active {
  color: var(--color-primary);
  font-weight: 600;
}

.article-form__author-row {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-sm);
}

.article-form__hint {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
}

.article-form__summary {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--spacing-sm) var(--spacing-md);
}

.article-form__summary dt {
  color: var(--color-text-secondary);
}

.article-form__summary dd {
  margin: 0;
}

.article-form__error {
  color: var(--color-error);
  font-size: var(--type-caption-size);
}

.article-form__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.article-form__save-state {
  font-size: var(--type-caption-size);
  color: var(--color-text-secondary);
}

.article-form__nav {
  display: flex;
  gap: var(--spacing-sm);
}

.btn {
  height: 40px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--type-button-size);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
}

.btn--primary[aria-disabled="true"] {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn--secondary {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}
</style>
