'use client';

import { useEffect, useState } from 'react';

import { getVaultStatus } from '@/lib/api';

export function useVaultStatus(account?: string) {
  const [status, setStatus] = useState<{ active?: boolean; deposit_usdc?: number } | null>(
    null
  );

  useEffect(() => {
    if (!account) return;
    getVaultStatus(account)
      .then((result) => setStatus(result))
      .catch(() => setStatus(null));
  }, [account]);

  return { status };
}
