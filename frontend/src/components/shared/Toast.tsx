// Use: Global toast notification system — success, error, loading, warning variants.

import { useState, useCallback, useMemo } from "react";
import { CheckCircle, XCircle, Loader2, AlertTriangle, X } from "lucide-react";
import { ToastCtx, type Toast, type ToastContextValue, type ToastType } from "./ToastContext";

let _idCounter = 0;
function genId() {
  return `toast-${++_idCounter}-${Date.now()}`;
}

const DURATIONS: Record<ToastType, number> = {
  success: 3000,
  error: 5000,
  warning: 4000,
  loading: 0, // persistent — must be dismissed manually
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const add = useCallback(
    (type: ToastType, message: string): string => {
      const id = genId();
      setToasts((prev) => [...prev, { id, type, message }]);
      const duration = DURATIONS[type];
      if (duration > 0) {
        setTimeout(() => dismiss(id), duration);
      }
      return id;
    },
    [dismiss]
  );

  const ctx: ToastContextValue = useMemo(() => ({
    success: (msg) => { add("success", msg); },
    error: (msg) => { add("error", msg); },
    loading: (msg) => add("loading", msg),
    warning: (msg) => { add("warning", msg); },
    dismiss,
  }), [add, dismiss]);

  return (
    <ToastCtx.Provider value={ctx}>
      {children}
      <div className="toast-container">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle size={18} color="var(--success)" />,
    error:   <XCircle size={18} color="var(--critical)" />,
    loading: <Loader2 size={18} color="var(--info)" className="btn-spinner" style={{ animation: "spin 1s linear infinite" }} />,
    warning: <AlertTriangle size={18} color="var(--warning)" />,
  };

  return (
    <div className={`toast toast-${toast.type}`} style={{ animation: "slideInRight 200ms ease" }}>
      <span className="toast-icon">{icons[toast.type]}</span>
      <span className="toast-message">{toast.message}</span>
      <button className="toast-close" onClick={onDismiss} aria-label="Dismiss">
        <X size={14} />
      </button>
    </div>
  );
}
