import { FetchError } from "ofetch";
import { useAuthStore } from "~/stores/auth";

export interface ApiFieldErrors {
  [field: string]: string[];
}

export class ApiError extends Error {
  code?: string;
  fieldErrors?: ApiFieldErrors;
  status?: number;

  constructor(message: string, opts: { code?: string; fieldErrors?: ApiFieldErrors; status?: number } = {}) {
    super(message);
    this.code = opts.code;
    this.fieldErrors = opts.fieldErrors;
    this.status = opts.status;
  }
}

/**
 * Thin $fetch wrapper: attaches the JWT access token, retries once after a
 * silent refresh on 401, and normalizes backend errors into ApiError
 * (TS section 10: unified {code, message, fieldErrors?} error format).
 */
export async function apiFetch<T>(path: string, options: Parameters<typeof $fetch>[1] = {}, _retried = false): Promise<T> {
  const config = useRuntimeConfig();
  const auth = useAuthStore();

  const headers = new Headers(options.headers as HeadersInit | undefined);
  if (auth.accessToken) {
    headers.set("Authorization", `Bearer ${auth.accessToken}`);
  }

  try {
    return await $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...options,
      headers,
    });
  } catch (err) {
    if (err instanceof FetchError) {
      if (err.response?.status === 401 && auth.refreshToken && !_retried) {
        const refreshed = await auth.refreshTokens();
        if (refreshed) {
          return apiFetch<T>(path, options, true);
        }
        auth.clear();
      }

      const data = err.response?._data as { code?: string; message?: string; fieldErrors?: ApiFieldErrors } | undefined;
      throw new ApiError(data?.message ?? err.message ?? "Ошибка сети", {
        code: data?.code,
        fieldErrors: data?.fieldErrors,
        status: err.response?.status,
      });
    }
    throw err;
  }
}
