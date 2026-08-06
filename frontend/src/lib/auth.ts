// Use: Auth helper functions — login, logout, token persistence, password reset flows.

import { api } from "./api";
import type { AuthUser } from "../types/auth";

// ─── Shapes ─────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface ValidateTokenResponse {
  valid: boolean;
  email: string | null;
}

export interface ExitRoleResponse {
  message: string;
  user: AuthUser;
}

export function getClientMacAddress(): string {
  try {
    const raw = `${navigator.userAgent}-${navigator.language}-${screen.width}x${screen.height}-${navigator.hardwareConcurrency || 4}-${screen.colorDepth}`;
    let hash = 0;
    for (let i = 0; i < raw.length; i++) {
      hash = (hash << 5) - hash + raw.charCodeAt(i);
      hash |= 0;
    }
    const hex = Math.abs(hash).toString(16).padStart(12, "0").toUpperCase();
    const formatted = hex.match(/.{1,2}/g)?.join(":") ?? "4A:8B:9C:2D:1E:0F";
    return formatted;
  } catch {
    return "4A:8B:9C:2D:1E:0F";
  }
}

export async function login(email: string, password: string, customMac?: string): Promise<LoginResponse> {
  const mac = customMac || getClientMacAddress();
  const res = await api.post<LoginResponse>(
    "/api/v1/auth/login",
    { email, password, mac_address: mac },
    { headers: { "X-Client-MAC": mac } }
  );
  return res.data;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const res = await api.get<AuthUser>("/api/v1/auth/me");
  return res.data;
}

export async function updateProfile(payload: {
  full_name?: string;
  phone?: string;
  designation?: string;
}): Promise<void> {
  await api.patch("/api/v1/auth/me", payload);
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await api.post("/api/v1/auth/change-password", {
    current_password: currentPassword,
    new_password: newPassword,
  });
}

export async function refreshSession(): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>("/api/v1/auth/refresh");
  return res.data;
}

export async function forgotPassword(email: string): Promise<void> {
  await api.post("/api/v1/auth/forgot-password", { email });
}

export async function validateResetToken(token: string): Promise<ValidateTokenResponse> {
  const res = await api.get<ValidateTokenResponse>("/api/v1/auth/validate-reset-token", {
    params: { token },
  });
  return res.data;
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await api.post("/api/v1/auth/reset-password", {
    token,
    new_password: newPassword,
  });
}

export async function logoutApi(): Promise<void> {
  await api.post("/api/v1/auth/logout");
}

export async function exitRoleAssumption(): Promise<ExitRoleResponse> {
  const res = await api.post<ExitRoleResponse>("/api/v1/auth/exit-role-assumption");
  return res.data;
}

// ─── Storage helpers (re-exported from storage.ts to keep backward compatibility) ─
export { persistSession, clearSessionStorage } from "./storage";

// ─── Role → dashboard mapping ────────────────────────────────────────────────

export function roleDashboard(roleName: string): string {
  const map: Record<string, string> = {
    "Super Admin":         "/super-admin/dashboard",
    "Institution Admin":   "/admin/dashboard",
    "Compliance Officer":  "/compliance/dashboard",
    "IT Security Officer": "/security/dashboard",
    "Auditor":             "/auditor/workspace",
    "Department Reviewer": "/dept/dashboard",
    "Vendor Reviewer":     "/vendor/dashboard",
    "Policy Approver":     "/policy/inbox",
    "Read-Only Assessor":  "/assessor/dashboard",
  };
  return map[roleName] ?? "/login";
}
