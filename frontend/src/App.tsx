import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import SearchPage from './pages/SearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ComparePage from './pages/ComparePage';
import SimilarPage from './pages/SimilarPage';
import LoginPage from './pages/LoginPage';
import CheckoutPage from './pages/CheckoutPage';
import AccountPage from './pages/AccountPage';
import { AuthProvider, useAuth } from './auth/AuthContext';
import Protected from './auth/Protected';
import { colors, typography, spacing, radius, transitions } from './styles/tokens';

const nav = [
  { path: '/', label: 'Select', icon: '🔍', el: <SearchPage />, premium: false },
  { path: '/analytics', label: 'Analytics', icon: '📊', el: <AnalyticsPage />, premium: true },
  { path: '/compare', label: 'Compare', icon: '⚔️', el: <ComparePage />, premium: true },
  { path: '/similar', label: 'Similar', icon: '🔄', el: <SimilarPage />, premium: true },
];

const routeElement = (n: typeof nav[number]) =>
  n.premium ? <Protected minTier="premium">{n.el}</Protected> : n.el;

const tierBadgeColor: Record<string, string> = {
  free: colors.gray500,
  premium: colors.primary500,
  admin: colors.accent500,
};

const AuthControls: React.FC = () => {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  if (loading) return null;

  if (!user) {
    return (
      <NavLink
        to="/login" data-testid="login-link"
        style={{
          fontSize: typography.fontSize.md, fontWeight: typography.fontWeight.semibold,
          color: colors.white, textDecoration: 'none',
          padding: `${spacing.xs}px ${spacing.base}px`, borderRadius: radius.md,
          background: `${colors.primary600}40`, border: `1px solid ${colors.primary500}66`,
        }}
      >
        Log in
      </NavLink>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
      <NavLink
        to="/account" data-testid="user-email"
        style={{ fontSize: typography.fontSize.sm, color: colors.gray300, textDecoration: 'none' }}
      >
        {user.email}
      </NavLink>
      <span
        data-testid="user-tier"
        style={{
          fontSize: typography.fontSize.xs, color: colors.white,
          background: tierBadgeColor[user.tier] || colors.gray600,
          padding: `2px ${spacing.sm}px`, borderRadius: radius.full,
          letterSpacing: '0.05em', textTransform: 'uppercase',
          fontWeight: typography.fontWeight.semibold,
        }}
      >
        {user.tier}
      </span>
      <button
        data-testid="logout-button"
        onClick={() => { logout(); navigate('/'); }}
        style={{
          fontSize: typography.fontSize.sm, fontWeight: typography.fontWeight.medium,
          color: colors.gray400, background: 'none', cursor: 'pointer',
          border: `1px solid ${colors.gray700}`, borderRadius: radius.md,
          padding: `${spacing.xs}px ${spacing.sm}px`, fontFamily: typography.fontFamily,
        }}
      >
        Log out
      </button>
    </div>
  );
};

const Layout: React.FC = () => (
  <div style={{ minHeight: '100vh', background: colors.gray50, fontFamily: typography.fontFamily }}>

    <header style={{
      background: `linear-gradient(135deg, ${colors.headerFrom} 0%, ${colors.headerTo} 100%)`,
      padding: `0 ${spacing['2xl']}px`,
      display: 'flex',
      alignItems: 'center',
      height: 60,
      position: 'sticky',
      top: 0,
      zIndex: 50,
      borderBottom: `1px solid ${colors.gray800}`,
      backdropFilter: 'blur(12px)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, marginRight: spacing['3xl'] }}>
        <div style={{
          width: 32, height: 32, borderRadius: radius.md,
          background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary400})`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16, fontWeight: typography.fontWeight.bold,
          color: colors.white,
          boxShadow: `0 0 16px ${colors.primary500}44`,
        }}>◓</div>
        <span style={{
          fontSize: typography.fontSize.xl,
          fontWeight: typography.fontWeight.bold,
          color: colors.white,
          letterSpacing: '-0.02em',
        }}>
          Poké<span style={{ color: colors.primary300 }}>Analytics</span>
        </span>
      </div>

      <nav data-testid="nav" style={{ display: 'flex', gap: 2 }}>
        {nav.map(n => (
          <NavLink key={n.path} to={n.path} end={n.path === '/'}
            data-testid={`nav-link-${n.label.toLowerCase()}`}
            style={({ isActive }) => ({
              padding: `${spacing.sm}px ${spacing.base}px`,
              borderRadius: radius.md,
              color: isActive ? colors.white : colors.gray400,
              textDecoration: 'none',
              fontWeight: isActive ? typography.fontWeight.semibold : typography.fontWeight.medium,
              fontSize: typography.fontSize.md,
              background: isActive ? `${colors.primary600}30` : 'transparent',
              transition: transitions.fast,
              display: 'flex',
              alignItems: 'center',
              gap: spacing.xs,
              letterSpacing: '-0.01em',
            })}>
            <span style={{ fontSize: '15px' }}>{n.icon}</span>
            {n.label}
          </NavLink>
        ))}
      </nav>

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: spacing.base }}>
        <AuthControls />
      </div>
    </header>

    <main style={{ maxWidth: 1440, margin: '0 auto', padding: `${spacing.xl}px ${spacing['2xl']}px` }}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/checkout" element={<Protected><CheckoutPage /></Protected>} />
        <Route path="/account" element={<Protected><AccountPage /></Protected>} />
        {nav.map(n => <Route key={n.path} path={n.path} element={routeElement(n)} />)}
      </Routes>
    </main>
  </div>
);

const App: React.FC = () => (
  <BrowserRouter>
    <AuthProvider>
      <Layout />
    </AuthProvider>
  </BrowserRouter>
);

export default App;
