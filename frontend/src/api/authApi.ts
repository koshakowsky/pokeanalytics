import { api } from './client';

export interface AuthUser {
  id: number;
  email: string;
  tier: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const registerApi = async (email: string, password: string): Promise<AuthUser> => {
  const { data } = await api.post('/auth/register', { email, password });
  return data;
};

export const loginApi = async (email: string, password: string): Promise<string> => {
  const { data } = await api.post<TokenResponse>('/auth/login', { email, password });
  return data.access_token;
};

export const getMe = async (): Promise<AuthUser> => {
  const { data } = await api.get('/auth/me');
  return data;
};
