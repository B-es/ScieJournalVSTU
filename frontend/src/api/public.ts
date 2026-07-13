import { apiFetch } from "~/api/http";
import type { ArticleAuthor } from "~/api/articles";

export interface PublicArticle {
  id: string;
  titleRu: string;
  titleEn: string;
  abstractRu: string;
  abstractEn: string;
  keywordsRu: string[];
  keywordsEn: string[];
  topic: string;
  doi: string;
  pagesCount: number | null;
  publishedAt: string;
  issueNumber: number | null;
  issueYear: number | null;
  authors: ArticleAuthor[];
}

export interface PublicArticleDetailResponse {
  article: PublicArticle;
  pdfUrl: string | null;
}

export interface PublicIssue {
  id: string;
  number: number;
  year: number;
  title: string;
  descriptionRu: string;
  descriptionEn: string;
  coverImageUrl: string | null;
  publishedAt: string;
  language: "ru" | "en" | "mixed";
  articlesCount: number;
  pagesCount: number;
  authorsCount: number;
}

export interface PublicIssueDetailResponse {
  issue: PublicIssue;
  articles: PublicArticle[];
}

export interface PublicArticleSearchParams {
  q?: string;
  keyword?: string;
  author?: string;
  topic?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
  [key: string]: string | number | undefined;
}

function toQuery(params: { [key: string]: string | number | undefined }): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== "");
  if (!entries.length) return "";
  const search = new URLSearchParams(entries.map(([k, v]) => [k, String(v)]));
  return `?${search.toString()}`;
}

/** US-10: search/archive listing — published articles only, no auth required. */
export function listPublicArticles(params: PublicArticleSearchParams = {}) {
  return apiFetch<{ items: PublicArticle[]; total: number }>(`/public/articles${toQuery(params)}`);
}

export function getPublicArticle(articleId: string) {
  return apiFetch<PublicArticleDetailResponse>(`/public/articles/${articleId}`);
}

/** US-12: bibliographic citation export. */
export function getCitation(articleId: string, format: "gost" | "apa" | "bibtex") {
  return apiFetch<{ format: string; citationText: string }>(
    `/public/articles/${articleId}/citation?format=${format}`,
  );
}

export function listPublicIssues(year?: number) {
  return apiFetch<{ items: PublicIssue[] }>(`/public/issues${toQuery({ year })}`);
}

export function getPublicIssue(issueId: string) {
  return apiFetch<PublicIssueDetailResponse>(`/public/issues/${issueId}`);
}
