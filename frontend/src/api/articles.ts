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
  completenessApprovedAt: string | null;
  publishedAt: string | null;
  issueId: string | null;
  issueNumber: number | null;
  issueYear: number | null;
  authors: ArticleAuthor[];
}

export interface EditorialDecisionItem {
  id: string;
  editorId: string;
  decision: "accept" | "reject" | "revise";
  comment: string;
  stage: "completeness_check" | "topic_check" | "review_decision";
  createdAt: string;
}

export interface ArticleReviewSummary {
  id: string;
  reviewerId: string;
  invitationStatus: "invited" | "accepted" | "declined";
  deadline: string;
  recommendation: "" | "accept" | "revise" | "reject";
  submittedAt: string | null;
  /** Only this sub-field of the reviewer's form data — never commentsForEditor (M3e plan #5). */
  commentsForAuthor: string;
}

export interface ArticleDetailResponse {
  article: ArticleDetail;
  versions: ArticleVersion[];
  reviews: ArticleReviewSummary[];
  decisions: EditorialDecisionItem[];
}

export interface RevisionUploadPayload {
  manuscriptFile: File;
  documents?: ArticleDocumentInput[];
  authorComment?: string;
}

export interface RevisionUploadResponse {
  versionId: string;
  status: string;
}

export interface TopicCheckPayload {
  approved: boolean;
  comment?: string;
}

export interface ReviewerAssignmentPayload {
  reviewerIds: string[];
  deadline: string;
}

export interface DecisionPayload {
  decision: "accept" | "reject" | "revise";
  comment: string;
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

/**
 * US-3: POST /api/articles/{id}/versions — files + author comment only, no
 * metadata (TS section 7), unlike the draft/submit payload.
 */
export function uploadRevisionVersion(articleId: string, payload: RevisionUploadPayload) {
  const form = new FormData();
  form.append("manuscriptFile", payload.manuscriptFile);
  if (payload.authorComment !== undefined) form.append("authorComment", payload.authorComment);
  if (payload.documents?.length) {
    const types: string[] = [];
    for (const doc of payload.documents) {
      form.append("documents", doc.file);
      types.push(doc.docType);
    }
    form.append("documentTypes", JSON.stringify(types));
  }
  return apiFetch<RevisionUploadResponse>(`/articles/${articleId}/versions`, { method: "POST", body: form });
}

/** US-4: POST /api/articles/{id}/topic-check (chief editor). */
export function topicCheck(articleId: string, payload: TopicCheckPayload) {
  return apiFetch<{ status: string }>(`/articles/${articleId}/topic-check`, {
    method: "POST",
    body: payload,
  });
}

/** US-4: POST /api/articles/{id}/reviewers (chief editor, >=2 reviewers). */
export function assignReviewers(articleId: string, payload: ReviewerAssignmentPayload) {
  return apiFetch<{ reviews: unknown[] }>(`/articles/${articleId}/reviewers`, {
    method: "POST",
    body: payload,
  });
}

/** US-7: POST /api/articles/{id}/decision (chief editor) — comment always required. */
export function makeDecision(articleId: string, payload: DecisionPayload) {
  return apiFetch<{ status: string }>(`/articles/${articleId}/decision`, {
    method: "POST",
    body: payload,
  });
}
