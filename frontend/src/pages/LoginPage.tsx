import React, { useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { colors, typography, spacing, radius, shadows } from '../styles/tokens';
import { card, inputStyle, labelStyle, pageTitle, pageSubtitle, errorBanner } from '../styles/ui';

type Mode = 'login' | 'register';

const messageFor = (err: any, mode: Mode): string => {
  const status = err?.response?.status;
  if (status === 401) return 'Invalid email or password.';
  if (status === 409) return 'This email is already registered.';
  if (status === 422) return 'Password must be at least 8 characters.';
  return mode === 'login' ? 'Login failed. Please try again.' : 'Registration failed. Please try again.';
};

const LoginPage: React.FC = () => {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const from = (location.state as { from?: string } | null)?.from || '/';

  // Already logged in (or just became so) - go to the intended destination,
  // not always home, so a login triggered by a deep link returns there.
  if (user) return <Navigate to={from} replace />;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === 'login') await login(email, password);
      else await register(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(messageFor(err, mode));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div data-testid="login-page" style={{ maxWidth: 420, margin: '48px auto' }}>
      <div style={card({ padding: spacing['2xl'] })}>
        <h1 style={pageTitle}>{mode === 'login' ? 'Welcome back' : 'Create account'}</h1>
        <p style={{ ...pageSubtitle, marginBottom: spacing.xl }}>
          {mode === 'login' ? 'Log in to access your account' : 'Sign up — new accounts start on the free tier'}
        </p>

        {error && <div data-testid="auth-error" style={errorBanner}>{error}</div>}

        <form onSubmit={submit}>
          <div style={{ marginBottom: spacing.md }}>
            <label htmlFor="auth-email" style={labelStyle}>Email</label>
            <input
              id="auth-email" data-testid="auth-email" type="email" required
              value={email} onChange={(e) => setEmail(e.target.value)}
              autoComplete="email" style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: spacing.xl }}>
            <label htmlFor="auth-password" style={labelStyle}>Password</label>
            <input
              id="auth-password" data-testid="auth-password" type="password" required
              value={password} onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              style={inputStyle}
            />
          </div>

          <button
            type="submit" data-testid="auth-submit" disabled={busy}
            style={{
              width: '100%',
              padding: `${spacing.base}px`,
              borderRadius: radius.lg,
              border: 'none',
              cursor: busy ? 'default' : 'pointer',
              background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary400})`,
              color: colors.white,
              fontSize: typography.fontSize.md,
              fontWeight: typography.fontWeight.semibold,
              fontFamily: typography.fontFamily,
              boxShadow: shadows.glow(colors.primary500),
              opacity: busy ? 0.6 : 1,
            }}
          >
            {busy ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Sign up'}
          </button>
        </form>

        <div style={{ marginTop: spacing.lg, textAlign: 'center', fontSize: typography.fontSize.sm, color: colors.gray500 }}>
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            data-testid="auth-toggle"
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              color: colors.primary600, fontWeight: typography.fontWeight.semibold,
              fontFamily: typography.fontFamily, fontSize: typography.fontSize.sm,
            }}
          >
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
