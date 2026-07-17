import { useAuthStore } from "~/stores/auth";

/**
 * Global route guard: gates every /cabinet/** route behind authentication
 * (TS section 8 role/permission matrix — cabinet is for authenticated
 * users only). Runs on both server and client thanks to the cookie-backed
 * auth store, so a direct request to a protected URL resolves correctly on
 * the very first render.
 */
export default defineNuxtRouteMiddleware((to) => {
  if (!to.path.startsWith("/cabinet")) return;

  const auth = useAuthStore();
  if (!auth.isAuthenticated) {
    return navigateTo({ path: "/login", query: { redirect: to.fullPath } });
  }
});
