/** Axios client with auth + 401 handling. */
import axios, { type AxiosError } from "axios";

import { useAuthStore } from "@/stores/auth";

export const api = axios.create({
  // Default: same-origin ("") — calls go to /api/v1/... on whatever host the
  // browser loaded (localhost, LAN IP, or a public tunnel). next.config.mjs
  // rewrites /api/* to the backend server-side, so the browser never needs to
  // reach :8000 directly. This is what makes phone / tunnel testing work and
  // removes the need for CORS. Set NEXT_PUBLIC_API_URL only to force an
  // absolute backend origin (e.g. a separately-hosted prod API).
  baseURL: process.env.NEXT_PUBLIC_API_URL || "",
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

// Attach JWT on each request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401 — but avoid redirect loops on public pages
const PUBLIC_PATHS = ["/signup", "/", "/terms", "/privacy", "/refund", "/language"];

api.interceptors.response.use(
  (resp) => resp,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth();
      if (typeof window !== "undefined") {
        const p = window.location.pathname;
        const isPublic = PUBLIC_PATHS.some(
          (pub) => p === pub || p.startsWith(pub + "/"),
        );
        if (!isPublic) {
          window.location.href = "/signup";
        }
      }
    }
    return Promise.reject(error);
  },
);

/** Extract user-readable error message from API response. */
export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    return error.message;
  }
  return error instanceof Error ? error.message : "Something went wrong";
}
