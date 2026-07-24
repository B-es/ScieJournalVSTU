import { apiFetch } from "~/api/http";

export interface ReviewArticleSummary {
  id: string;
  titleRu: string;
  titleEn: string;
  abstractRu: string;
  topic: string;
}

export interface ReviewItem {
  id: string;
  article: ReviewArticleSummary;
  reviewerId: string;
  reviewerFullName: string;
  reviewerEmail: string;
  invitationStatus: "invited" | "accepted" | "declined" | "cancelled";
  deadline: string;
  recommendation: string;
  submittedAt: string | null;
}

export interface ReviewerCandidate {
  id: string;
  fullName: string;
  email: string;
}

/** US-5: GET /api/reviews — own invitations, or (chief editor) every invitation sent. */
export function listMyReviews(statusFilter?: string, articleId?: string) {
  const params = new URLSearchParams();
  if (statusFilter) params.set("status", statusFilter);
  if (articleId) params.set("article", articleId);
  const query = params.toString() ? `?${params.toString()}` : "";
  // Trailing slash required, same APPEND_SLASH note as api/articles.ts's listArticles.
  return apiFetch<{ items: ReviewItem[] }>(`/reviews/${query}`);
}

/** US-5: POST /api/reviews/{id}/respond. */
export function respondToInvitation(reviewId: string, accepted: boolean) {
  return apiFetch<{ status: string }>(`/reviews/${reviewId}/respond`, {
    method: "POST",
    body: { accepted },
  });
}

/** US-4/US-5: POST /api/reviews/{id}/reassign (chief editor). */
export function reassignReviewer(reviewId: string, newReviewerId: string, deadline: string) {
  return apiFetch<{ reviewId: string; status: string }>(`/reviews/${reviewId}/reassign`, {
    method: "POST",
    body: { newReviewerId, deadline },
  });
}

/** M3c plan decision #5: GET /api/users/reviewers (chief editor's reviewer picker). */
export function listReviewerCandidates() {
  return apiFetch<{ items: ReviewerCandidate[] }>("/users/reviewers");
}

export interface ReviewFormData {
  commentsForAuthor: string;
  commentsForEditor?: string;
}

export interface SubmitReviewPayload {
  recommendation: "accept" | "revise" | "reject";
  formData: ReviewFormData;
  reviewFile?: File;
  evaluationRating?: Record<string, string>;
  languageQuality?: string;
  conflictOfInterest?: boolean | null;
  plagiarismDetected?: boolean | null;
  ethicalIssues?: boolean | null;
  articleRating?: Record<string, string>;
}

/** US-6: POST /api/reviews/{id}/submit. */
export function submitReview(reviewId: string, payload: SubmitReviewPayload) {
  const form = new FormData();
  form.append("recommendation", payload.recommendation);
  form.append("formData", JSON.stringify(payload.formData));
  if (payload.reviewFile) form.append("reviewFile", payload.reviewFile);
  
  if (payload.evaluationRating) {
    form.append("evaluationRating", JSON.stringify(payload.evaluationRating));
  }
  if (payload.languageQuality) {
    form.append("languageQuality", payload.languageQuality);
  }
  if (payload.conflictOfInterest !== undefined && payload.conflictOfInterest !== null) {
    form.append("conflictOfInterest", String(payload.conflictOfInterest));
  }
  if (payload.plagiarismDetected !== undefined && payload.plagiarismDetected !== null) {
    form.append("plagiarismDetected", String(payload.plagiarismDetected));
  }
  if (payload.ethicalIssues !== undefined && payload.ethicalIssues !== null) {
    form.append("ethicalIssues", String(payload.ethicalIssues));
  }
  if (payload.articleRating) {
    form.append("articleRating", JSON.stringify(payload.articleRating));
  }
  
  return apiFetch<{ status: string }>(`/reviews/${reviewId}/submit`, { 
    method: "POST", 
    body: form 
  });
}