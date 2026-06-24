// Use: Reset Password page — validates token on load, shows form with live validation checklist.

import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Eye, EyeOff, CheckCircle, XCircle, Check, AlertCircle } from "lucide-react";
import { validateResetToken, resetPassword } from "../../lib/auth";

type PageState = "loading" | "invalid" | "form" | "success";

interface PwRule { label: string; test: (pw: string) => boolean; }
const PW_RULES: PwRule[] = [
  { label: "At least 8 characters",       test: (p) => p.length >= 8 },
  { label: "At least one uppercase letter",test: (p) => /[A-Z]/.test(p) },
  { label: "At least one number",          test: (p) => /[0-9]/.test(p) },
];

export default function ResetPassword() {
  const { token } = useParams<{ token: string }>();
  const navigate  = useNavigate();

  const [pageState, setPageState] = useState<PageState>("loading");
  const [email, setEmail]         = useState<string | null>(null);

  const [newPw, setNewPw]         = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [showNew, setShowNew]     = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);

  // Validate token on mount
  useEffect(() => {
    if (!token) { setPageState("invalid"); return; }
    validateResetToken(token)
      .then((res) => {
        if (res.valid) {
          setEmail(res.email);
          setPageState("form");
        } else {
          setPageState("invalid");
        }
      })
      .catch(() => setPageState("invalid"));
  }, [token]);

  const allRulesPassed = PW_RULES.every((r) => r.test(newPw));
  const passwordsMatch = newPw === confirmPw && confirmPw.length > 0;
  const canSubmit = allRulesPassed && passwordsMatch;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit || !token) return;
    setError(null);
    setLoading(true);
    try {
      await resetPassword(token, newPw);
      setPageState("success");
      // Auto-redirect to /login after 2 seconds
      setTimeout(() => navigate("/login", { replace: true }), 2000);
    } catch {
      setError("This link has expired. Please request a new one.");
    } finally {
      setLoading(false);
    }
  }

  // ── Loading state ─────────────────────────────────────────────────────────
  if (pageState === "loading") {
    return (
      <div className="auth-form-box" style={{ textAlign: "center", paddingTop: 60 }}>
        <div className="btn-spinner" style={{ width: 32, height: 32, margin: "0 auto 16px", borderWidth: 3 }} />
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Validating your reset link…</p>
      </div>
    );
  }

  // ── Invalid token ─────────────────────────────────────────────────────────
  if (pageState === "invalid") {
    return (
      <div className="auth-form-box" id="reset-invalid-state">
        <div className="error-state">
          <div className="error-icon-circle">
            <XCircle size={36} />
          </div>
          <h1 className="success-title" style={{ color: "#0F172A" }}>
            Link expired or invalid
          </h1>
          <p className="success-desc">
            This password reset link has expired or has already been used.
          </p>
          <Link to="/forgot-password" id="request-new-link-btn" style={{ display: "block", marginTop: 24 }}>
            <button className="btn btn-primary btn-full btn-lg">Request a new link</button>
          </Link>
        </div>
      </div>
    );
  }

  // ── Success state ─────────────────────────────────────────────────────────
  if (pageState === "success") {
    return (
      <div className="auth-form-box" id="reset-success-state">
        <div className="success-state">
          <div className="success-icon-circle">
            <CheckCircle size={36} />
          </div>
          <h1 className="success-title">Password updated!</h1>
          <p className="success-desc">
            Your password has been reset successfully.
            You'll be redirected to login in a moment.
          </p>
        </div>
      </div>
    );
  }

  // ── Form ──────────────────────────────────────────────────────────────────
  return (
    <div className="auth-form-box" id="reset-password-form-container">
      <h1 className="auth-form-title">Set new password</h1>
      {email && (
        <p className="auth-form-subtitle">
          Resetting password for <strong>{email}</strong>
        </p>
      )}

      <form className="auth-form-fields" onSubmit={handleSubmit} style={{ marginTop: 32 }} noValidate>
        {/* New password */}
        <div className="form-group">
          <label htmlFor="reset-new-password" className="form-label">New password</label>
          <div className="form-input-wrapper">
            <input
              id="reset-new-password"
              type={showNew ? "text" : "password"}
              className="form-input form-input-with-icon"
              placeholder="••••••••"
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
              autoFocus
            />
            <button
              type="button"
              className="form-input-icon-right"
              onClick={() => setShowNew((v) => !v)}
              aria-label={showNew ? "Hide password" : "Show password"}
            >
              {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          {/* Live validation checklist */}
          {newPw.length > 0 && (
            <div className="pw-rules">
              {PW_RULES.map((rule) => {
                const passed = rule.test(newPw);
                return (
                  <div key={rule.label} className={`pw-rule ${passed ? "passed" : ""}`}>
                    <div className="pw-rule-dot">
                      {passed && <Check size={8} strokeWidth={3} />}
                    </div>
                    {rule.label}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Confirm password */}
        <div className="form-group">
          <label htmlFor="reset-confirm-password" className="form-label">Confirm new password</label>
          <div className="form-input-wrapper">
            <input
              id="reset-confirm-password"
              type={showConfirm ? "text" : "password"}
              className={`form-input form-input-with-icon ${
                confirmPw.length > 0 && !passwordsMatch ? "error" : ""
              }`}
              placeholder="••••••••"
              value={confirmPw}
              onChange={(e) => setConfirmPw(e.target.value)}
            />
            <button
              type="button"
              className="form-input-icon-right"
              onClick={() => setShowConfirm((v) => !v)}
              aria-label={showConfirm ? "Hide password" : "Show password"}
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {confirmPw.length > 0 && !passwordsMatch && (
            <div className="inline-error">
              <AlertCircle size={12} /> Passwords do not match
            </div>
          )}
        </div>

        {/* API error */}
        {error && (
          <div className="lock-banner" role="alert">
            <AlertCircle size={16} className="lock-banner-icon" />
            <div className="lock-banner-text">
              {error}{" "}
              <Link to="/forgot-password" style={{ fontWeight: 700 }}>
                Request new link
              </Link>
            </div>
          </div>
        )}

        <button
          id="set-new-password-btn"
          type="submit"
          className="btn btn-primary btn-full btn-lg"
          disabled={!canSubmit || loading}
        >
          {loading && <span className="btn-spinner" />}
          Set New Password
        </button>
      </form>
    </div>
  );
}
