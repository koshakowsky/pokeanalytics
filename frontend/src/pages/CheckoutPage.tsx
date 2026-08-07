import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { validateCard, detectBrand, normalizeNumber, type FieldErrors } from '../auth/cardValidation';
import { getPlans, checkout, type Plan } from '../api/billingApi';
import { colors, typography, spacing, radius, shadows } from '../styles/tokens';
import { card, inputStyle, labelStyle, pageTitle, pageSubtitle, errorBanner } from '../styles/ui';

// One key per form lifetime so a double-click or retry doesn't charge twice.
const makeIdemKey = () => `checkout-${Date.now()}-${Math.random().toString(36).slice(2)}`;

const formatPrice = (p: Plan) =>
  `${(p.price_cents / 100).toFixed(2)} ${p.currency.toUpperCase()} / ${p.interval}`;

const CheckoutPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();

  const [plans, setPlans] = useState<Plan[]>([]);
  const [number, setNumber] = useState('');
  const [expMonth, setExpMonth] = useState('');
  const [expYear, setExpYear] = useState('');
  const [cvc, setCvc] = useState('');

  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [idemKey] = useState(makeIdemKey);

  useEffect(() => { getPlans().then(setPlans).catch(() => setFormError('Failed to load plans.')); }, []);

  const plan = plans[0];
  const brand = useMemo(() => detectBrand(normalizeNumber(number)), [number]);

  const alreadyPremium = user && user.tier !== 'free';

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const fields = {
      number,
      exp_month: Number(expMonth),
      exp_year: Number(expYear),
      cvc,
    };
    const errs = validateCard(fields);
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setBusy(true);
    try {
      await checkout({ plan_id: plan.id, card: fields, idempotency_key: idemKey });
      await refreshUser();
      navigate('/account', { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setFormError(detail?.message || 'Checkout failed. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  if (alreadyPremium) {
    return (
      <div data-testid="checkout-page" style={{ maxWidth: 480, margin: '48px auto', textAlign: 'center' }}>
        <div style={card({ padding: spacing['2xl'] })}>
          <div style={{ fontSize: 40, marginBottom: spacing.md }}>✅</div>
          <h1 style={pageTitle}>You're on {user!.tier}</h1>
          <p style={{ ...pageSubtitle, marginBottom: spacing.xl }}>All premium features are already unlocked.</p>
          <button data-testid="go-account" onClick={() => navigate('/account')} style={primaryBtn}>
            Manage subscription
          </button>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="checkout-page" style={{ maxWidth: 460, margin: '32px auto' }}>
      <div style={{ marginBottom: spacing.lg }}>
        <h1 style={pageTitle}>Upgrade to Premium</h1>
        <p style={pageSubtitle}>Unlock analytics, comparison and similarity tools.</p>
      </div>

      {plan && (
        <div data-testid="plan-card" style={card({ padding: spacing.lg, marginBottom: spacing.lg })}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <span style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900 }}>
              {plan.name}
            </span>
            <span data-testid="plan-price" style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.primary600 }}>
              {formatPrice(plan)}
            </span>
          </div>
        </div>
      )}

      <form onSubmit={submit} style={card({ padding: spacing.lg })}>
        {formError && <div data-testid="checkout-error" style={errorBanner}>{formError}</div>}

        <div style={{ marginBottom: spacing.md }}>
          <label htmlFor="card-number" style={labelStyle}>
            Card number {brand !== 'unknown' && number && <span data-testid="card-brand" style={{ color: colors.primary600 }}>· {brand}</span>}
          </label>
          <input
            id="card-number" data-testid="card-number" inputMode="numeric"
            placeholder="4242 4242 4242 4242"
            value={number} onChange={(e) => setNumber(e.target.value)} style={inputStyle}
          />
          {fieldErrors.number && <FieldError testid="error-number" msg={fieldErrors.number} />}
        </div>

        <div style={{ display: 'flex', gap: spacing.md, marginBottom: spacing.xl }}>
          <div style={{ flex: 1 }}>
            <label htmlFor="exp-month" style={labelStyle}>Exp. month</label>
            <input id="exp-month" data-testid="exp-month" inputMode="numeric" placeholder="MM"
              value={expMonth} onChange={(e) => setExpMonth(e.target.value)} style={inputStyle} />
          </div>
          <div style={{ flex: 1 }}>
            <label htmlFor="exp-year" style={labelStyle}>Exp. year</label>
            <input id="exp-year" data-testid="exp-year" inputMode="numeric" placeholder="YYYY"
              value={expYear} onChange={(e) => setExpYear(e.target.value)} style={inputStyle} />
          </div>
          <div style={{ flex: 1 }}>
            <label htmlFor="cvc" style={labelStyle}>CVC</label>
            <input id="cvc" data-testid="cvc" inputMode="numeric" placeholder="123"
              value={cvc} onChange={(e) => setCvc(e.target.value)} style={inputStyle} />
          </div>
        </div>
        {(fieldErrors.expiry || fieldErrors.cvc) && (
          <div style={{ marginTop: -spacing.md, marginBottom: spacing.md }}>
            {fieldErrors.expiry && <FieldError testid="error-expiry" msg={fieldErrors.expiry} />}
            {fieldErrors.cvc && <FieldError testid="error-cvc" msg={fieldErrors.cvc} />}
          </div>
        )}

        <button type="submit" data-testid="pay-button" disabled={busy || !plan} style={{ ...primaryBtn, width: '100%', opacity: busy ? 0.6 : 1 }}>
          {busy ? 'Processing…' : plan ? `Pay ${formatPrice(plan)}` : 'Loading…'}
        </button>
        <p style={{ ...pageSubtitle, fontSize: typography.fontSize.xs, marginTop: spacing.md, textAlign: 'center' }}>
          Demo checkout — no real payment is taken. Use 4242 4242 4242 4242 to succeed.
        </p>
      </form>
    </div>
  );
};

const FieldError: React.FC<{ testid: string; msg: string }> = ({ testid, msg }) => (
  <div data-testid={testid} style={{ color: colors.error, fontSize: typography.fontSize.xs, marginTop: 4 }}>
    {msg}
  </div>
);

const primaryBtn: React.CSSProperties = {
  padding: `${spacing.base}px ${spacing.xl}px`,
  borderRadius: radius.lg, border: 'none', cursor: 'pointer',
  background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary400})`,
  color: colors.white, fontSize: typography.fontSize.md,
  fontWeight: typography.fontWeight.semibold, fontFamily: typography.fontFamily,
  boxShadow: shadows.glow(colors.primary500),
};

export default CheckoutPage;
