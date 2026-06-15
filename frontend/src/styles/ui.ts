import React from 'react';
import { colors, typography, spacing, radius, shadows, transitions } from './tokens';

// ── Shared UI style helpers ──────────────────────────────────────────
// Common building blocks reused across pages so the same card / input /
// dropdown / tooltip styling is defined once instead of per-page.

export const card = (extra?: React.CSSProperties): React.CSSProperties => ({
  background: colors.white,
  borderRadius: radius.xl,
  border: `1px solid ${colors.gray200}`,
  boxShadow: shadows.md,
  ...extra,
});

export const inputStyle: React.CSSProperties = {
  width: '100%', padding: '8px 12px', borderRadius: radius.sm,
  border: `1px solid ${colors.gray200}`, fontSize: typography.fontSize.md,
  fontFamily: typography.fontFamily, color: colors.gray800,
  background: colors.white, transition: transitions.fast,
  outline: 'none', boxSizing: 'border-box',
};

export const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: typography.fontSize.xs,
  fontWeight: typography.fontWeight.semibold, color: colors.gray400,
  marginBottom: 4, letterSpacing: '0.04em', textTransform: 'uppercase',
};

// Larger rounded search box used by the Compare / Similar pages.
export const searchInputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 16px', borderRadius: radius.lg,
  border: `2px solid ${colors.gray200}`, fontSize: typography.fontSize.md,
  fontFamily: typography.fontFamily, color: colors.gray800,
  outline: 'none', transition: transitions.fast, boxSizing: 'border-box',
};

export const dropdownPanel: React.CSSProperties = {
  position: 'absolute', top: '100%', left: 0, right: 0, marginTop: 4,
  background: colors.white, border: `1px solid ${colors.gray200}`, borderRadius: radius.lg,
  boxShadow: shadows.lg, zIndex: 20, maxHeight: 320, overflowY: 'auto',
};

export const dropdownRow: React.CSSProperties = {
  display: 'flex', alignItems: 'center', padding: `${spacing.sm}px ${spacing.md}px`,
  cursor: 'pointer', borderBottom: `1px solid ${colors.gray100}`, transition: transitions.fast,
};

// Recharts tooltip styling.
export const tooltipStyle = {
  contentStyle: {
    background: colors.gray900, border: 'none', borderRadius: radius.md,
    fontSize: typography.fontSize.sm, color: colors.white, padding: '8px 12px',
    boxShadow: shadows.lg,
  },
  itemStyle: { color: colors.gray200 },
};

export const pageTitle: React.CSSProperties = {
  fontSize: typography.fontSize['3xl'], fontWeight: typography.fontWeight.extrabold,
  color: colors.gray900, letterSpacing: '-0.03em', marginBottom: 4,
};

export const pageSubtitle: React.CSSProperties = {
  fontSize: typography.fontSize.md, color: colors.gray500,
};

// Small inline error banner.
export const errorBanner: React.CSSProperties = {
  padding: `${spacing.sm}px ${spacing.base}px`, borderRadius: radius.md,
  background: '#fef2f2', border: `1px solid ${colors.error}33`,
  color: colors.error, fontSize: typography.fontSize.sm,
  marginBottom: spacing.md,
};
