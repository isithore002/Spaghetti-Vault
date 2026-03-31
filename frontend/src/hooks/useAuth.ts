'use client';

import { usePrivy } from '@privy-io/react-auth';

type AuthState = {
  authenticated: boolean;
  user: { wallet?: { address?: string } } | null;
  login: () => void;
  logout: () => void;
  signMessage: (args: { message: string }) => Promise<string | { signature: string }>;
};

export function useAuth(): AuthState {
  const { authenticated, user, login, logout, signMessage } = usePrivy();
  return {
    authenticated,
    user,
    login,
    logout,
    signMessage,
  };
}
