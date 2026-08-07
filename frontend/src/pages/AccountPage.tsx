import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { getSubscription, cancelSubscription, type Subscription } from '../api/billingApi';
import { colors, typography, spacing, radius, shadows } from '../styles/tokens';
import { card, pageTitle, pageSubtitle, errorBanner } from '../styles/ui';

const AccountPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();

  const [sub, setSub] = useState<Subscription | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => getSubscription().then(setSub).catch(() => setError('Failed to load subscription.'));
  useEffect(() => { load(); }, []);

  const onCancel = async () => {
    setBusy(true);
    setError(null);
    try {
      await cancelSubscription();
      await refreshUser();
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.detail?.message || 'Cancel failed.');
    } finally {
      setBusy(false);
    }
  };

  const isActive = sub?.status === 'active';

  return (
    <div data-testid="account-page" style={{ maxWidth: 520, margin: '32px auto' }}>
      <div style={{ marginBottom: spacing.lg }}>
        <h1 style={pageTitle}>Account</h1>
        <p style={pageSubtitle}>Manage your plan and subscription.</p>
      </div>

      {error && <div style={errorBanner}>{error}</div>}

      {/* ── Profile ── */}
      <div style={card({ padding: spacing.lg, marginBottom: spacing.lg })}>
        <Row label="Email" value={user?.email ?? '—'} testid="account-email" />
        <Row label="Tier" value={<TierBadge tier={user?.tier ?? 'free'} />} testid="account-tier" />
      </div>

      {/* ── Subscription ── */}
      <div style={card({ padding: spacing.lg })}>
        <h2 style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.md }}>
          Subscription
        </h2>

        {sub === null ? (
          <p style={pageSubtitle}>Loading…</p>
        ) : sub.status === 'none' ? (
          <div data-testid="sub-none">
            <p style={{ ...pageSubtitle, marginBottom: spacing.md }}>You don't have a subscription yet.</p>
            <button data-testid="upgrade-cta" onClick={() => navigate('/checkout')} style={primaryBtn}>
              Upgrade to Premium
            </button>
          </div>
        ) : (
          <div data-testid="sub-details">
            <Row label="Status" value={<span data-testid="sub-status" style={{ textTransform: 'capitalize' }}>{sub.status}</span>} testid="row-status" />
            <Row label="Plan" value={sub.plan ?? '—'} testid="row-plan" />
            <Row label="Card" value={sub.card_brand ? `${sub.card_brand} •••• ${sub.card_last4}` : '—'} testid="row-card" />
            <Row label="Renews" value={sub.current_period_end ? new Date(sub.current_period_end).toLocaleDateString() : '—'} testid="row-renews" />

            <div style={{ marginTop: spacing.lg }}>
              {isActive ? (
                <button data-testid="cancel-button" onClick={onCancel} disabled={busy} style={{ ...dangerBtn, opacity: busy ? 0.6 : 1 }}>
                  {busy ? 'Cancelling…' : 'Cancel subscription'}
                </button>
              ) : (
                <button data-testid="resubscribe-button" onClick={() => navigate('/checkout')} style={primaryBtn}>
                  Re-subscribe
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const Row: React.FC<{ label: string; value: React.ReactNode; testid: string }> = ({ label, value, testid }) => (
  <div data-testid={testid} style={{ display: 'flex', justifyContent: 'space-between', padding: `${spacing.sm}px 0`, borderBottom: `1px solid ${colors.gray100}` }}>
    <span style={{ color: colors.gray500, fontSize: typography.fontSize.sm }}>{label}</span>
    <span style={{ color: colors.gray900, fontSize: typography.fontSize.md, fontWeight: typography.fontWeight.medium }}>{value}</span>
  </div>
);

const tierColor: Record<string, string> = { free: colors.gray500, premium: colors.primary500, admin: colors.accent500 };
const TierBadge: React.FC<{ tier: string }> = ({ tier }) => (
  <span style={{
    fontSize: typography.fontSize.xs, color: colors.white, background: tierColor[tier] || colors.gray600,
    padding: `2px ${spacing.sm}px`, borderRadius: radius.full, textTransform: 'uppercase',
    letterSpacing: '0.05em', fontWeight: typography.fontWeight.semibold,
  }}>{tier}</span>
);

const primaryBtn: React.CSSProperties = {
  padding: `${spacing.sm}px ${spacing.lg}px`, borderRadius: radius.lg, border: 'none', cursor: 'pointer',
  background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary400})`, color: colors.white,
  fontSize: typography.fontSize.md, fontWeight: typography.fontWeight.semibold,
  fontFamily: typography.fontFamily, boxShadow: shadows.glow(colors.primary500),
};

const dangerBtn: React.CSSProperties = {
  padding: `${spacing.sm}px ${spacing.lg}px`, borderRadius: radius.lg, cursor: 'pointer',
  background: colors.white, color: colors.error, border: `1px solid ${colors.error}55`,
  fontSize: typography.fontSize.md, fontWeight: typography.fontWeight.semibold, fontFamily: typography.fontFamily,
};

export default AccountPage;
