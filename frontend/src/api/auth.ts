import { apiFetch } from "~/api/http";

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface RegisterResponse {
  userId: string;
  token: TokenPair;
}

export interface LoginResponse {
  token: TokenPair;
  roles: string[];
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  affiliation: string;
  orcid: string;
  language_pref: "ru" | "en";
  roles: string[];
}

export function register(fullName: string, email: string, password: string) {
  return apiFetch<RegisterResponse>("/auth/register", {
    method: "POST",
    body: { fullName, email, password },
  });
}

export function login(email: string, password: string) {
  return apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function logout(refresh: string) {
  return apiFetch<{ status: string }>("/auth/logout", {
    method: "POST",
    body: { refresh },
  });
}

export function refreshTokenPair(refresh: string) {
  // _retried=true: a failing refresh call must never trigger apiFetch's own
  // 401 -> refresh -> retry loop (that loop would call back into this
  // function and recurse indefinitely).
  return apiFetch<TokenPair>(
    "/auth/refresh",
    {
      method: "POST",
      body: { refresh },
    },
    true,
  );
}

export function fetchMe() {
  return apiFetch<CurrentUser>("/auth/me");
}
