// Use: Axios API client instance configured with interceptors for the main backend service.

import axios from "axios";
import { useAuthStore } from "../store/authStore";
import { persistSession, clearSessionStorage } from "./storage";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // send HttpOnly cookies for refresh token
});

// ─── Request interceptor — attach Bearer token ──────────────────────────────
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Response interceptor — silent token refresh on 401 ────────────────────
let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: any) => void;
}> = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // Do NOT trigger silent refresh for login, register, or refresh endpoint errors
    const isAuthEndpoint =
      original?.url?.includes("/api/v1/auth/login") ||
      original?.url?.includes("/api/v1/auth/register") ||
      original?.url?.includes("/api/v1/auth/refresh");

    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              original.headers.Authorization = `Bearer ${token}`;
              resolve(api(original));
            },
            reject: (err) => {
              reject(err);
            },
          });
        });
      }

      isRefreshing = true;
      const { setSession, clearSession } = useAuthStore.getState();

      try {
        const res = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, undefined, {
          withCredentials: true,
        });
        const { access_token, user: newUser } = res.data;
        setSession(access_token, newUser);
        persistSession(newUser);

        refreshQueue.forEach((item) => item.resolve(access_token));
        refreshQueue = [];
        original.headers.Authorization = `Bearer ${access_token}`;
        return api(original);
      } catch (refreshErr) {
        refreshQueue.forEach((item) => item.reject(refreshErr));
        refreshQueue = [];
        clearSession();
        clearSessionStorage();
        window.location.href = "/login";
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Re-export storage helpers for convenience
export { persistSession, clearSessionStorage };
