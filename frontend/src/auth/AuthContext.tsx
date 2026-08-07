import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getToken, setToken, setUnauthorizedHandler } from '../api/client';
import {
  loginApi, registerApi, getMe, type AuthUser,
} from '../api/authApi';

export const TIER_ORDER: Record<string, number> = { free: 0, premium: 1, admin: 2 };

export const hasTier = (userTier: string | undefined, minTier: string): boolean =>
  (TIER_ORDER[userTier ?? ''] ?? -1) >= TIER_ORDER[minTier];

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    if (!getToken()) {
      setLoading(false);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const token = await loginApi(email, password);
    setToken(token);
    setUser(await getMe());
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    // register does not return a token, so log in right after to get a session.
    await registerApi(email, password);
    const token = await loginApi(email, password);
    setToken(token);
    setUser(await getMe());
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    setUser(await getMe());
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
