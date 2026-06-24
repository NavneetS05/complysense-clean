// Use: Zustand store managing authentication token, user details, active role state, and dark mode.

import { create } from "zustand";
import type { AuthUser } from "../types/auth";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isHydrated: boolean;
  setSession: (token: string, refreshToken: string, user: AuthUser) => void;
  updateUser: (user: AuthUser) => void;
  clearSession: () => void;
  setHydrated: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  refreshToken: null,
  user: null,
  isHydrated: false,
  setSession: (token, refreshToken, user) =>
    set({ token, refreshToken, user }),
  updateUser: (user) => set({ user }),
  clearSession: () =>
    set({ token: null, refreshToken: null, user: null }),
  setHydrated: () => set({ isHydrated: true }),
}));

// ─── Notification store ────────────────────────────────────────────────────

export interface Notification {
  notification_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  related_entity_id?: string;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  setNotifications: (n: Notification[]) => void;
  setUnreadCount: (c: number) => void;
  markAllRead: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,
  setNotifications: (notifications) => set({ notifications }),
  setUnreadCount: (unreadCount) => set({ unreadCount }),
  markAllRead: () =>
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),
}));

// ─── Dark mode store ────────────────────────────────────────────────────────

interface ThemeState {
  dark: boolean;
  toggleDark: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  dark: (() => {
    try {
      const saved = localStorage.getItem("cs_dark");
      if (saved !== null) return saved === "true";
      return window.matchMedia("(prefers-color-scheme: dark)").matches;
    } catch {
      return false;
    }
  })(),
  toggleDark: () => {
    const next = !get().dark;
    set({ dark: next });
    try {
      localStorage.setItem("cs_dark", String(next));
      document.documentElement.classList.toggle("dark", next);
    } catch { /* */ }
  },
}));
