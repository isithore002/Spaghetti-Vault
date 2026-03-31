export function sortJsonKeys(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sortJsonKeys);
  }
  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => [k, sortJsonKeys(v)]);
    return Object.fromEntries(entries);
  }
  return value;
}

export function buildSigningMessage(input: object): string {
  const sorted = sortJsonKeys(input);
  return JSON.stringify(sorted);
}

export function isPacificaAccount(address?: string | null): boolean {
  if (!address) {
    return false;
  }

  // Pacifica account ids are Solana-style base58 public keys (typically 32-44 chars).
  if (address.startsWith('0x')) {
    return false;
  }

  return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
}
