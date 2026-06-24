// Use: Axios API client instance configured with interceptors for the main backend service.

import axios from "axios";
import { useAuthStore } from "../store/authStore";

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
let refreshQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;
      const { refreshToken, setSession, clearSession, user } =
        useAuthStore.getState();

      if (!refreshToken) {
        clearSession();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token, user: newUser } = res.data;
        setSession(access_token, refresh_token, newUser);
        persistSession(access_token, refresh_token, newUser);

        refreshQueue.forEach((cb) => cb(access_token));
        refreshQueue = [];
        original.headers.Authorization = `Bearer ${access_token}`;
        return api(original);
      } catch {
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

// Helpers re-exported here to avoid circular imports in some call sites
import { persistSession, clearSessionStorage } from "./auth";
export { persistSession, clearSessionStorage };
