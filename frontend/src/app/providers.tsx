'use client';

import { PrivyProvider } from '@privy-io/react-auth';

export function Providers({ children }: { children: React.ReactNode }) {
  const appId = process.env.NEXT_PUBLIC_PRIVY_APP_ID || '';
  if (!appId || appId.startsWith('REPLACE_')) {
    return (
      <div style={{ padding: 24, color: '#fff', background: '#111' }}>
        Missing NEXT_PUBLIC_PRIVY_APP_ID in frontend/.env.local
      </div>
    );
  }

  return (
    <PrivyProvider
      appId={appId}
      config={{
        loginMethods: ['wallet'],
        appearance: { theme: 'light', accentColor: '#ec5b2d' },
        embeddedWallets: { createOnLogin: 'off' },
      }}
    >
      {children}
    </PrivyProvider>
  );
}
