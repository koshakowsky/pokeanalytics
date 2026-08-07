// Client-side card checks mirroring the backend (api/billing_cards.py) for
// instant form feedback. The backend re-validates; these are pure functions so
// they stay easy to test.

export const normalizeNumber = (n: string): string => n.replace(/[\s-]/g, '');

export const luhnValid = (number: string): boolean => {
  if (!/^\d+$/.test(number)) return false;
  let sum = 0;
  for (let i = 0; i < number.length; i++) {
    let d = Number(number[number.length - 1 - i]);
    if (i % 2 === 1) {
      d *= 2;
      if (d > 9) d -= 9;
    }
    sum += d;
  }
  return sum % 10 === 0;
};

export const detectBrand = (number: string): string => {
  if (number.startsWith('4')) return 'visa';
  if (['34', '37'].includes(number.slice(0, 2))) return 'amex';
  const two = Number(number.slice(0, 2));
  if (two >= 51 && two <= 55) return 'mastercard';
  const four = Number(number.slice(0, 4));
  if (four >= 2221 && four <= 2720) return 'mastercard';
  return 'unknown';
};

export const cvcLength = (brand: string): number => (brand === 'amex' ? 4 : 3);

export interface CardFields {
  number: string;
  exp_month: number;
  exp_year: number;
  cvc: string;
}

export type FieldErrors = Partial<Record<'number' | 'expiry' | 'cvc', string>>;

export const validateCard = (fields: CardFields): FieldErrors => {
  const errors: FieldErrors = {};
  const num = normalizeNumber(fields.number);

  if (!/^\d+$/.test(num) || num.length < 13 || num.length > 19) {
    errors.number = 'Card number must be 13–19 digits.';
  } else if (!luhnValid(num)) {
    errors.number = 'Card number is invalid.';
  }

  const now = new Date();
  const curYear = now.getFullYear();
  const curMonth = now.getMonth() + 1;
  if (!(fields.exp_month >= 1 && fields.exp_month <= 12)) {
    errors.expiry = 'Expiry month must be between 1 and 12.';
  } else if (
    fields.exp_year < curYear ||
    (fields.exp_year === curYear && fields.exp_month < curMonth)
  ) {
    errors.expiry = 'The card has expired.';
  }

  const brand = detectBrand(num);
  const need = cvcLength(brand);
  if (!/^\d+$/.test(fields.cvc) || fields.cvc.length !== need) {
    errors.cvc = `CVC must be ${need} digits.`;
  }

  return errors;
};
