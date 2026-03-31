export function WalletButton({
  onClick,
  label,
  disabled = false,
}: {
  onClick: () => void;
  label: string;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="cyber-button rounded-xl px-6 py-3 disabled:cursor-not-allowed disabled:opacity-60"
    >
      {label}
    </button>
  );
}
