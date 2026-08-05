import { createContext, useContext } from "react";

export type ToastType = "success" | "error" | "loading" | "warning";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

export interface ToastContextValue {
  success: (msg: string) => void;
  error: (msg: string) => void;
  loading: (msg: string) => string;
  dismiss: (id: string) => void;
  warning: (msg: string) => void;
}

export const ToastCtx = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastCtx);
  if (!ctx) throw new Error("useToast must be used inside <ToastProvider>");
  return ctx;
}
