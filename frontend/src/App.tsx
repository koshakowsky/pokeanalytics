import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import SearchPage from './pages/SearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ComparePage from './pages/ComparePage';
import SimilarPage from './pages/SimilarPage';
import { colors, typography, spacing, radius, transitions } from './styles/tokens';

const nav = [
  { path: '/', label: 'Select', icon: '🔍', el: <SearchPage /> },
  { path: '/analytics', label: 'Analytics', icon: '📊', el: <AnalyticsPage /> },
  { path: '/compare', label: 'Compare', icon: '⚔️', el: <ComparePage /> },
  { path: '/similar', label: 'Similar', icon: '🔄', el: <SimilarPage /> },
];

const App: React.FC = () => (
  <BrowserRouter>
    <div style={{ minHeight: '100vh', background: colors.gray50, fontFamily: typography.fontFamily }}>

      {/* ── Header ── */}
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
        {/* Logo */}
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

        {/* Nav */}
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

        {/* Right side badge */}
        <div style={{ marginLeft: 'auto' }}>
          <span style={{
            fontSize: typography.fontSize.xs,
            color: colors.gray500,
            background: colors.gray800,
            padding: `2px ${spacing.sm}px`,
            borderRadius: radius.full,
            border: `1px solid ${colors.gray700}`,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}>
            Gen I
          </span>
        </div>
      </header>

      {/* ── Content ── */}
      <main style={{ maxWidth: 1440, margin: '0 auto', padding: `${spacing.xl}px ${spacing['2xl']}px` }}>
        <Routes>
          {nav.map(n => <Route key={n.path} path={n.path} element={n.el} />)}
        </Routes>
      </main>
    </div>
  </BrowserRouter>
);

export default App;
