'use client';

import { useCallback, useState } from 'react';

import { getDashboard } from '@/lib/api';

export type DashboardData = {
  position: any;
  current_funding_rate: number;
  annualised_funding_apy: number;
  total_funding_earned: number;
  trade_count: number;
  funding_history: Array<{ rate: number; ts: number }>;
};

export function useFundingRate(account?: string) {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!account) {
      setLoading(false);
      return;
    }
    try {
      const data = await getDashboard(account);
      setDashboard(data);
    } finally {
      setLoading(false);
    }
  }, [account]);

  return { dashboard, loading, refresh };
}
