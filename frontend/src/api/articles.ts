import { apiFetch } from "~/api/http";

export interface ArticleAuthorInput {
  fullName: string;
  affiliation?: string;
  email?: string;
}

export interface ArticleDocumentInput {
  file: File;
  docType: string;
}

export interface ArticleDraftPayload {
  articleId?: string;
  titleRu?: string;
  titleEn?: string;
  abstractRu?: string;
  abstractEn?: string;
  keywordsRu?: string[];
  keywordsEn?: string[];
  topic?: string;
  authors?: ArticleAuthorInput[];
  manuscriptFile?: File;
  documents?: ArticleDocumentInput[];
}

export interface DraftResponse {
  articleId: string;
  status: string;
  lastAutosavedAt: string;
}

export interface SubmitResponse {
  articleId: string;
  status: string;
}

export interface ArticleListItem {
  id: string;
  titleRu: string;
  titleEn: string;
  status: string;
  topic: string;
  createdAt: string;
  updatedAt: string;
}

export interface ArticleAuthor {
  id: string;
  fullName: string;
  affiliation: string;
  email: string;
  order: number;
}

export interface ArticleDocument {
  id: string;
  docType: string;
  fileUrl: string;
}

export interface ArticleVersion {
  id: string;
  versionNumber: number;
  manuscriptFileUrl: string;
  submittedAt: string;
  authorComment: string;
  documents: ArticleDocument[];
}

export interface ArticleDetail {
  id: string;
  titleRu: string;
  titleEn: string;
  abstractRu: string;
  abstractEn: string;
  keywordsRu: string[];
  keywordsEn: string[];
  topic: string;
  status: string;
  doi: string;
  pagesCount: number | null;
  createdAt: string;
  updatedAt: string;
  lastAutosavedAt: string | null;
  authors: ArticleAuthor[];
}

export interface ArticleDetailResponse {
  article: ArticleDetail;
  versions: ArticleVersion[];
  reviews: unknown[];
  decisions: unknown[];
}

/**
 * `keywordsRu`/`keywordsEn`/`authors` are JSON-encoded into string fields
 * (the backend's ArticleDraftInputSerializer.JSONStringField), and documents
 * travel as parallel `documents` (files) / `documentTypes` (JSON array)
 * fields — see M3 plan decision #3.
 */
function buildFormData(payload: ArticleDraftPayload): FormData {
  const form = new FormData();
  if (payload.articleId) form.append("articleId", payload.articleId);
  if (payload.titleRu !== undefined) form.append("titleRu", payload.titleRu);
  if (payload.titleEn !== undefined) form.append("titleEn", payload.titleEn);
  if (payload.abstractRu !== undefined) form.append("abstractRu", payload.abstractRu);
  if (payload.abstractEn !== undefined) form.append("abstractEn", payload.abstractEn);
  if (payload.keywordsRu !== undefined) form.append("keywordsRu", JSON.stringify(payload.keywordsRu));
  if (payload.keywordsEn !== undefined) form.append("keywordsEn", JSON.stringify(payload.keywordsEn));
  if (payload.topic !== undefined) form.append("topic", payload.topic);
  if (payload.authors !== undefined) form.append("authors", JSON.stringify(payload.authors));
  if (payload.manuscriptFile) form.append("manuscriptFile", payload.manuscriptFile);
  if (payload.documents?.length) {
    const types: string[] = [];
    for (const doc of payload.documents) {
      form.append("documents", doc.file);
      types.push(doc.docType);
    }
    form.append("documentTypes", JSON.stringify(types));
  }
  return form;
}

export function saveDraft(payload: ArticleDraftPayload) {
  return apiFetch<DraftResponse>("/articles/draft", { method: "POST", body: buildFormData(payload) });
}

export function submitArticle(articleId: string, payload: ArticleDraftPayload = {}) {
  return apiFetch<SubmitResponse>(`/articles/${articleId}/submit`, {
    method: "POST",
    body: buildFormData(payload),
  });
}

export function listArticles(statusFilter?: string) {
  const query = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : "";
  // Trailing slash required — Django's list route is "/api/articles/";
  // without it, APPEND_SLASH 301-redirects and turns the GET into a
  // cross-origin redirect that (depending on client) can drop the auth header.
  return apiFetch<{ items: ArticleListItem[] }>(`/articles/${query}`);
}

export function getArticle(articleId: string) {
  return apiFetch<ArticleDetailResponse>(`/articles/${articleId}`);
}
