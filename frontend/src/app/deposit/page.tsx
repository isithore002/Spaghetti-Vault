'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { deposit } from '@/lib/api';
import { WalletButton } from '@/components/WalletButton';
import { useAuth } from '@/hooks/useAuth';

const ESTIMATED_APY = {
  conservative: { apy: '8-12%', maxDrawdown: '3%', leverage: '2x' },
};

export default function DepositPage() {
  const { user, authenticated, login } = useAuth();
  const router = useRouter();
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [connectingWallet, setConnectingWallet] = useState(false);
  const [error, setError] = useState('');
  const connectLockTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const walletAddress = user?.wallet?.address;

  useEffect(() => {
    if (authenticated) {
      setConnectingWallet(false);
      if (connectLockTimer.current) {
        clearTimeout(connectLockTimer.current);
        connectLockTimer.current = null;
      }
    }

    return () => {
      if (connectLockTimer.current) {
        clearTimeout(connectLockTimer.current);
        connectLockTimer.current = null;
      }
    };
  }, [authenticated]);

  async function handleDeposit() {
    if (!walletAddress || !amount) return;

    setLoading(true);
    setError('');
    try {
      await deposit(walletAddress, parseFloat(amount));
      router.push('/authorize');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Deposit failed';
      if (message.includes('Network Error') || message.includes('CORS')) {
        setError('Backend request blocked. Ensure API is running and FRONTEND_ORIGINS includes http://localhost:3001.');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleWalletConnect() {
    if (connectingWallet) {
      return;
    }

    setError('');
    setConnectingWallet(true);
    if (connectLockTimer.current) {
      clearTimeout(connectLockTimer.current);
    }
    connectLockTimer.current = setTimeout(() => {
      setConnectingWallet(false);
      connectLockTimer.current = null;
    }, 12_000);

    try {
      await Promise.resolve(login());
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Wallet connection failed';
      setError(message);
      if (connectLockTimer.current) {
        clearTimeout(connectLockTimer.current);
        connectLockTimer.current = null;
      }
      setConnectingWallet(false);
    }
  }

  if (!authenticated) {
    return (
      <div className="cyber-shell flex min-h-screen flex-col items-center justify-center p-6">
        <h1 className="font-cyber text-5xl font-bold">FluxVault</h1>
        <p className="cyber-muted mt-2">Enter the funding-rate vault interface</p>
        <div className="mt-8">
          <WalletButton
            onClick={handleWalletConnect}
            label={connectingWallet ? 'Connecting...' : 'Connect Wallet'}
            disabled={connectingWallet}
          />
        </div>
        {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
      </div>
    );
  }

  return (
    <div className="cyber-shell flex min-h-screen items-center justify-center p-6">
      <div className="cyber-panel w-full max-w-md space-y-6 rounded-3xl p-8 backdrop-blur-sm">
        <h2 className="font-cyber text-2xl font-semibold">Deposit // FluxVault</h2>
        <p className="cyber-muted text-sm">
          Connected: {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
        </p>

        <div>
          <label className="cyber-muted mb-1 block text-sm">Amount (USDC)</label>
          <input
            type="number"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="100"
            className="w-full rounded-xl border border-orange-300/25 bg-black/40 px-4 py-3 text-orange-50 outline-none focus:border-orange-300"
          />
        </div>

        <div className="space-y-2 rounded-xl border border-orange-400/25 bg-orange-500/5 p-4 text-sm">
          <div className="flex justify-between">
            <span className="cyber-muted">Strategy</span>
            <span>Carry Trade (Conservative)</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Est. APY</span>
            <span className="text-orange-300">{ESTIMATED_APY.conservative.apy}</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Max drawdown</span>
            <span>{ESTIMATED_APY.conservative.maxDrawdown}</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Leverage</span>
            <span>{ESTIMATED_APY.conservative.leverage}</span>
          </div>
        </div>

        {error && <p className="text-sm text-red-300">{error}</p>}

        <button
          onClick={handleDeposit}
          disabled={loading || !amount}
          className="cyber-button w-full rounded-xl py-3 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Deposit & Continue'}
        </button>
      </div>
    </div>
  );
}
