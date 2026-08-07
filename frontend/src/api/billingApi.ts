import { api } from './client';

export interface Plan {
  id: string;
  name: string;
  price_cents: number;
  currency: string;
  interval: string;
}

export interface Subscription {
  status: string;
  plan: string | null;
  card_brand: string | null;
  card_last4: string | null;
  current_period_end: string | null;
}

export interface CardInput {
  number: string;
  exp_month: number;
  exp_year: number;
  cvc: string;
}

export interface CheckoutPayload {
  plan_id: string;
  card: CardInput;
  idempotency_key?: string;
}

export const getPlans = async (): Promise<Plan[]> => {
  const { data } = await api.get('/billing/plans');
  return data;
};

export const getSubscription = async (): Promise<Subscription> => {
  const { data } = await api.get('/billing/subscription');
  return data;
};

export const checkout = async (payload: CheckoutPayload): Promise<Subscription> => {
  const { data } = await api.post('/billing/checkout', payload);
  return data;
};

export const cancelSubscription = async (): Promise<Subscription> => {
  const { data } = await api.post('/billing/cancel');
  return data;
};
