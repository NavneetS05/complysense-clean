// Use: Login page — email/password with lockout countdown, role-based redirect.

import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Eye, EyeOff, Lock, AlertCircle } from "lucide-react";
import { useAuthStore } from "../../store/authStore";
import { login, persistSession, roleDashboard } from "../../lib/auth";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setSession, user } = useAuthStore();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw]     = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [lockedUntil, setLockedUntil] = useState<Date | null>(null);
  const [countdown, setCountdown]     = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // If already logged in, redirect immediately
  useEffect(() => {
    if (user) navigate(roleDashboard(user.role_name), { replace: true });
  }, [user, navigate]);

  // Countdown tick
  useEffect(() => {
    if (!lockedUntil) return;
    function tick() {
      const rem = Math.ceil((lockedUntil!.getTime() - Date.now()) / 1000);
      if (rem <= 0) {
        setLockedUntil(null);
        setCountdown(0);
        if (timerRef.current) clearInterval(timerRef.current);
      } else {
        setCountdown(rem);
      }
    }
    tick();
    timerRef.current = setInterval(tick, 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [lockedUntil]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (lockedUntil && Date.now() < lockedUntil.getTime()) return;
    setError(null);
    setLoading(true);
    try {
      const data = await login(email, password);
      setSession(data.access_token, data.user);
      persistSession(data.user);
      const from = (location.state as { from?: { pathname: string } })?.from?.pathname;
      navigate(from ?? roleDashboard(data.user.role_name), { replace: true });
    } catch (err: unknown) {
      const status = (err as { response?: { status: number; data?: { blocked_until?: string } } })
        ?.response?.status;
      const detail = (err as { response?: { data?: { blocked_until?: string } } })
        ?.response?.data;

      if (status === 423 || status === 429) {
        const blockedUntil = detail?.blocked_until ?? (detail as { error?: { blocked_until?: string } })?.error?.blocked_until;
        const until = blockedUntil
          ? new Date(blockedUntil)
          : new Date(Date.now() + 5000);
        setLockedUntil(until);
        setError("Too many failed attempts. Account temporarily locked.");
      } else if (status === 403) {
        setError("Your account has been deactivated. Contact your administrator.");
      } else {
        setError("Invalid email or password.");
      }
    } finally {
      setLoading(false);
    }
  }

  const isLocked = lockedUntil ? Date.now() < lockedUntil.getTime() : false;

  return (
    <div className="auth-form-box" id="login-form-container">
      <h1 className="auth-form-title">Welcome back</h1>
      <p className="auth-form-subtitle">Sign in to your ComplySense account</p>

      {/* Lockout banner */}
      {isLocked && (
        <div className="lock-banner" style={{ marginBottom: 20 }} role="alert">
          <Lock size={16} className="lock-banner-icon" />
          <div className="lock-banner-text">
            Account locked due to failed attempts.{" "}
            Try again in <span className="lock-countdown">{countdown}s</span>
          </div>
        </div>
      )}

      <form className="auth-form-fields" onSubmit={handleSubmit} noValidate>
        {/* Email */}
        <div className="form-group">
          <label htmlFor="login-email" className="form-label">Email address</label>
          <input
            id="login-email"
            type="email"
            className={`form-input ${error && !isLocked ? "error" : ""}`}
            placeholder="you@institution.ac.in"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            autoFocus
          />
        </div>

        {/* Password */}
        <div className="form-group">
          <label htmlFor="login-password" className="form-label">Password</label>
          <div className="form-input-wrapper">
            <input
              id="login-password"
              type={showPw ? "text" : "password"}
              className={`form-input form-input-with-icon ${error && !isLocked ? "error" : ""}`}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
            <button
              type="button"
              className="form-input-icon-right"
              onClick={() => setShowPw((v) => !v)}
              aria-label={showPw ? "Hide password" : "Show password"}
            >
              {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {error && !isLocked && (
            <div className="inline-error" id="login-error-msg" role="alert">
              <AlertCircle size={12} /> {error}
            </div>
          )}
        </div>

        {/* Submit */}
        <button
          id="login-submit-btn"
          type="submit"
          className="btn btn-primary btn-full btn-lg"
          disabled={loading || isLocked || !email || !password}
          style={{ marginTop: 4 }}
        >
          {loading && <span className="btn-spinner" />}
          {isLocked ? `Locked (${countdown}s)` : "Sign In"}
        </button>
      </form>

      <div className="auth-form-footer">
        <Link to="/forgot-password" id="forgot-password-link">Forgot password?</Link>
      </div>
    </div>
  );
}
