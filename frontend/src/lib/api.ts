import axios from 'axios';
import { isPacificaAccount } from './pacifica';

const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: BASE });

export async function deposit(wallet: string, amount: number) {
  const { data } = await api.post('/vault/deposit', {
    wallet_address: wallet,
    amount_usdc: amount,
  });
  return data;
}

export async function checkApproval(account: string) {
  if (!isPacificaAccount(account)) {
    return { approved: false, builder_code: 'SPAGHETTIVAULT1' };
  }
  const { data } = await api.get(`/builder/check?account=${account}`);
  return data as { approved: boolean; builder_code: string };
}

export async function submitApproval(signedPayload: object) {
  const { data } = await api.post('/builder/approve', signedPayload);
  return data;
}

export async function submitRevocation(signedPayload: object) {
  const { data } = await api.post('/builder/revoke', signedPayload);
  return data;
}

export async function getDashboard(account: string) {
  const { data } = await api.get(`/dashboard/summary?account=${account}`);
  return data;
}

export async function getVaultStatus(account: string) {
  const { data } = await api.get(`/vault/status?account=${account}`);
  return data;
}
