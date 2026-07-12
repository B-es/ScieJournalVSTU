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
  invitationStatus: "invited" | "accepted" | "declined";
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
export function listMyReviews(statusFilter?: string) {
  const query = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : "";
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
}

/** US-6: POST /api/reviews/{id}/submit. */
export function submitReview(reviewId: string, payload: SubmitReviewPayload) {
  const form = new FormData();
  form.append("recommendation", payload.recommendation);
  form.append("formData", JSON.stringify(payload.formData));
  if (payload.reviewFile) form.append("reviewFile", payload.reviewFile);
  return apiFetch<{ status: string }>(`/reviews/${reviewId}/submit`, { method: "POST", body: form });
}
