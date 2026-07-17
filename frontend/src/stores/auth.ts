import { defineStore } from "pinia";
import * as authApi from "~/api/auth";
import type { CurrentUser } from "~/api/auth";

const COOKIE_OPTS = { default: () => null, maxAge: 60 * 60 * 24 * 7, sameSite: "lax" as const };

/**
 * Setup-style store so we can use `useCookie` (SSR-aware) instead of
 * localStorage: localStorage isn't readable during server-side rendering, so
 * a direct request to a /cabinet/** route would always look "logged out" on
 * the server and the auth middleware would bounce an already-authenticated
 * user back to /login before hydration ever runs. Cookies avoid that.
 */
export const useAuthStore = defineStore("auth", () => {
  const accessToken = useCookie<string | null>("sj_access", COOKIE_OPTS);
  const refreshToken = useCookie<string | null>("sj_refresh", COOKIE_OPTS);
  const user = useCookie<CurrentUser | null>("sj_user", COOKIE_OPTS);

  const isAuthenticated = computed(() => !!accessToken.value);
  const roles = computed(() => user.value?.roles ?? []);
  function hasRole(code: string) {
    return roles.value.includes(code);
  }

  function clear() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
  }

  async function fetchMe() {
    user.value = await authApi.fetchMe();
  }

  async function register(fullName: string, email: string, password: string) {
    const res = await authApi.register(fullName, email, password);
    accessToken.value = res.token.access;
    refreshToken.value = res.token.refresh;
    await fetchMe();
  }

  async function login(email: string, password: string) {
    const res = await authApi.login(email, password);
    accessToken.value = res.token.access;
    refreshToken.value = res.token.refresh;
    await fetchMe();
  }

  async function logout() {
    if (refreshToken.value) {
      try {
        await authApi.logout(refreshToken.value);
      } catch {
        // Best-effort: still clear local state even if the blacklist call fails.
      }
    }
    clear();
  }

  /** Returns true if the access token was successfully renewed. */
  async function refreshTokens(): Promise<boolean> {
    if (!refreshToken.value) return false;
    try {
      const pair = await authApi.refreshTokenPair(refreshToken.value);
      accessToken.value = pair.access;
      refreshToken.value = pair.refresh;
      return true;
    } catch {
      return false;
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    roles,
    hasRole,
    clear,
    fetchMe,
    register,
    login,
    logout,
    refreshTokens,
  };
});
