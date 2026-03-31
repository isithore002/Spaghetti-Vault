'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { checkApproval, submitApproval, submitRevocation } from '@/lib/api';
import { buildSigningMessage, isPacificaAccount } from '@/lib/pacifica';
import { RevokeButton } from '@/components/RevokeButton';
import { useAuth } from '@/hooks/useAuth';

const BUILDER_CODE = 'FLUXVAULT1';
const MAX_FEE_RATE = '0.001';

function buildApprovalMessage(timestamp: number): object {
  return {
    data: {
      builder_code: BUILDER_CODE,
      max_fee_rate: MAX_FEE_RATE,
    },
    expiry_window: 5_000,
    timestamp,
    type: 'approve_builder_code',
  };
}

function buildRevocationMessage(timestamp: number): object {
  return {
    data: { builder_code: BUILDER_CODE },
    expiry_window: 5_000,
    timestamp,
    type: 'revoke_builder_code',
  };
}

export default function AuthorizePage() {
  const { user, signMessage } = useAuth();
  const router = useRouter();
  const [approved, setApproved] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  const walletAddress = user?.wallet?.address;
  const walletSupported = isPacificaAccount(walletAddress);

  useEffect(() => {
    if (!walletAddress || !walletSupported) {
      setApproved(false);
      return;
    }
    checkApproval(walletAddress)
      .then((result) => setApproved(result.approved))
      .catch(() => setApproved(false));
  }, [walletAddress, walletSupported]);

  async function signCompactMessage(message: object): Promise<string> {
    const compact = buildSigningMessage(message);
    const signatureResult = await signMessage({ message: compact });

    if (typeof signatureResult === 'string') {
      return signatureResult;
    }
    if (signatureResult && typeof signatureResult === 'object' && 'signature' in signatureResult) {
      return String((signatureResult as { signature: string }).signature);
    }
    throw new Error('Wallet did not return a signature');
  }

  async function handleApprove() {
    if (!walletAddress || !walletSupported) {
      setStatus('Connect a Solana wallet to authorize SpaghettiVault on Pacifica.');
      return;
    }
    setLoading(true);
    setStatus('Waiting for wallet signature...');

    try {
      const timestamp = Date.now();
      const signature = await signCompactMessage(buildApprovalMessage(timestamp));
      const payload = {
        account: walletAddress,
        agent_wallet: null,
        signature,
        timestamp,
        expiry_window: 5_000,
        builder_code: BUILDER_CODE,
        max_fee_rate: MAX_FEE_RATE,
      };

      setStatus('Submitting to Pacifica...');
      await submitApproval(payload);
      setApproved(true);
      setStatus('Authorization complete. Redirecting...');
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Approval failed';
      setStatus(`Error: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke() {
    if (!walletAddress || !walletSupported) {
      setStatus('Connect a Solana wallet to manage Pacifica builder permissions.');
      return;
    }
    setLoading(true);
    setStatus('Waiting for wallet signature...');

    try {
      const timestamp = Date.now();
      const signature = await signCompactMessage(buildRevocationMessage(timestamp));
      const payload = {
        account: walletAddress,
        agent_wallet: null,
        signature,
        timestamp,
        expiry_window: 5_000,
        builder_code: BUILDER_CODE,
      };

      setStatus('Revoking...');
      await submitRevocation(payload);
      setApproved(false);
      setStatus('Access revoked.');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Revocation failed';
      setStatus(`Error: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cyber-shell flex min-h-screen items-center justify-center p-6">
      <div className="cyber-panel w-full max-w-md space-y-6 rounded-3xl p-8 backdrop-blur-sm">
        <h2 className="font-cyber text-2xl font-semibold">Authorize // Builder Code</h2>

        <div className="space-y-3 rounded-xl border border-orange-400/30 bg-orange-500/5 p-5 text-sm">
          <p className="cyber-muted leading-relaxed">
            SpaghettiVault uses Pacifica Builder Program permissions to trade on your behalf. You can revoke at any time.
          </p>
          <div className="flex justify-between">
            <span className="cyber-muted">Builder code</span>
            <span className="font-mono">{BUILDER_CODE}</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Max leverage</span>
            <span>3x</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Max fee rate</span>
            <span>0.1%</span>
          </div>
          <div className="flex justify-between">
            <span className="cyber-muted">Revocable</span>
            <span className="text-orange-300">Yes, anytime</span>
          </div>
        </div>

        {!walletSupported && walletAddress && (
          <div className="rounded-xl border border-amber-300/45 bg-amber-500/10 p-3 text-sm text-amber-100">
            Connected wallet appears to be EVM ({walletAddress.slice(0, 6)}...). Pacifica requires a Solana address.
          </div>
        )}

        {approved === true && (
          <div className="rounded-xl border border-orange-300/45 bg-orange-400/10 p-3 text-sm text-orange-200">
            Vault is authorized and running.
          </div>
        )}

        {status && <p className="cyber-muted text-sm">{status}</p>}

        {approved !== true ? (
          <button
            onClick={handleApprove}
            disabled={loading || !walletSupported}
            className="cyber-button w-full rounded-xl py-3 disabled:opacity-50"
          >
            {loading ? 'Signing...' : 'Sign & Authorize Vault'}
          </button>
        ) : (
          <div className="space-y-3">
            <button
              onClick={() => router.push('/dashboard')}
              className="cyber-button w-full rounded-xl py-3"
            >
              View Dashboard
            </button>
            <RevokeButton onClick={handleRevoke} loading={loading} />
          </div>
        )}
      </div>
    </div>
  );
}
