'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { PositionCard } from '@/components/PositionCard';
import { FundingChart } from '@/components/FundingChart';
import { useFundingRate } from '@/hooks/useFundingRate';
import { useVaultStatus } from '@/hooks/useVaultStatus';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardPage() {
  const { authenticated, user, logout } = useAuth();
  const router = useRouter();
  const wallet = user?.wallet?.address;

  const { loading, dashboard, refresh } = useFundingRate(wallet);
  const { status } = useVaultStatus(wallet);

  useEffect(() => {
    if (!authenticated) {
      router.push('/');
      return;
    }

    void refresh();
    const interval = setInterval(() => {
      void refresh();
    }, 15_000);

    return () => clearInterval(interval);
  }, [authenticated, refresh, router]);

  if (loading) {
    return (
      <div className="cyber-shell flex min-h-screen items-center justify-center">
        <p className="cyber-muted">Loading dashboard...</p>
      </div>
    );
  }

  const fundingPct = ((dashboard?.current_funding_rate ?? 0) * 100).toFixed(4);
  const apyPct = ((dashboard?.annualised_funding_apy ?? 0) * 100).toFixed(2);

  return (
    <div className="cyber-shell min-h-screen p-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-cyber text-3xl font-semibold">SpaghettiVault Dashboard</h1>
          <div className="flex gap-2">
            <button
              onClick={() => router.push('/authorize')}
              className="rounded-lg border border-orange-400/40 px-3 py-1.5 text-sm text-orange-100"
            >
              Manage Access
            </button>
            <button
              onClick={logout}
              className="rounded-lg border border-orange-200/25 bg-orange-500/10 px-3 py-1.5 text-sm text-orange-100"
            >
              Disconnect
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <StatCard label="Funding APY" value={`${apyPct}%`} sub="annualized" />
          <StatCard
            label="Funding earned"
            value={`$${(dashboard?.total_funding_earned ?? 0).toFixed(4)}`}
            sub="total USDC"
          />
          <StatCard
            label="Current rate"
            value={`${fundingPct}%`}
            sub="per hour"
            valueClass={Number(fundingPct) > 0 ? 'text-mint' : 'text-red-300'}
          />
        </div>

        <PositionCard position={dashboard?.position ?? null} />
        <FundingChart points={dashboard?.funding_history ?? []} />

        <div className="rounded-xl border border-orange-400/25 bg-orange-500/5 p-4 text-sm text-orange-50/85">
          <p>Deposit active: {status?.active ? 'Yes' : 'No'}</p>
          <p>Trades executed: {dashboard?.trade_count ?? 0}</p>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  valueClass = 'text-white',
}: {
  label: string;
  value: string;
  sub: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-2xl border border-orange-400/25 bg-orange-500/5 p-5">
      <p className="cyber-muted text-xs">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${valueClass}`}>{value}</p>
      <p className="cyber-muted mt-1 text-xs">{sub}</p>
    </div>
  );
}
