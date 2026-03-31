export function RevokeButton({ onClick, loading }: { onClick: () => void; loading: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="w-full rounded-xl border border-orange-300/45 bg-transparent py-3 font-semibold text-orange-100 transition hover:bg-orange-400/10 disabled:opacity-50"
    >
      {loading ? 'Revoking...' : 'Revoke Access'}
    </button>
  );
}
