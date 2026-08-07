import React from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, hasTier } from './AuthContext';
import { colors, typography, spacing, radius, shadows } from '../styles/tokens';
import { card, pageTitle, pageSubtitle } from '../styles/ui';

interface ProtectedProps {
  minTier?: string;
  children: React.ReactNode;
}

const Protected: React.FC<ProtectedProps> = ({ minTier, children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div data-testid="auth-loading" style={{ padding: spacing.xl, color: colors.gray400 }}>Loading…</div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (minTier && !hasTier(user.tier, minTier)) {
    return <UpgradePrompt minTier={minTier} />;
  }

  return <>{children}</>;
};

const UpgradePrompt: React.FC<{ minTier: string }> = ({ minTier }) => {
  const navigate = useNavigate();

  return (
    <div data-testid="upgrade-prompt" style={{ maxWidth: 520, margin: '48px auto', textAlign: 'center' }}>
      <div style={card({ padding: spacing['2xl'] })}>
        <div style={{ fontSize: 40, marginBottom: spacing.md }}>✨</div>
        <h1 style={pageTitle}>Premium feature</h1>
        <p style={{ ...pageSubtitle, marginBottom: spacing.xl }}>
          This section requires the <strong>{minTier}</strong> tier. Upgrade to unlock
          analytics, comparison and similarity tools.
        </p>

        <button
          data-testid="view-plans-button"
          onClick={() => navigate('/checkout')}
          style={{
            padding: `${spacing.base}px ${spacing.xl}px`,
            borderRadius: radius.lg,
            border: 'none',
            cursor: 'pointer',
            background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary400})`,
            color: colors.white,
            fontSize: typography.fontSize.md,
            fontWeight: typography.fontWeight.semibold,
            fontFamily: typography.fontFamily,
            boxShadow: shadows.glow(colors.primary500),
          }}
        >
          View plans
        </button>
      </div>
    </div>
  );
};

export default Protected;
