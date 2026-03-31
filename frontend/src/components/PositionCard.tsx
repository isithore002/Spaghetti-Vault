type Position = {
  size?: string;
  unrealised_pnl?: string | number;
  margin_ratio?: number;
} | null;

export function PositionCard({ position }: { position: Position }) {
  return (
    <div className="rounded-2xl border border-orange-400/25 bg-orange-500/5 p-6">
      <h3 className="font-cyber mb-4 text-sm text-orange-100">Active Position</h3>
      {position ? (
        <div className="space-y-2 text-sm">
          <Row label="Market" value="SOL-PERP" />
          <Row label="Side" value="Short" />
          <Row label="Size" value={`${position.size ?? '0'} SOL`} />
          <Row
            label="Unrealized PnL"
            value={`$${Number(position.unrealised_pnl ?? 0).toFixed(4)}`}
            valueClass={Number(position.unrealised_pnl ?? 0) >= 0 ? 'text-orange-300' : 'text-red-300'}
          />
          <Row
            label="Margin health"
            value={`${((position.margin_ratio ?? 0) * 100).toFixed(2)}%`}
          />
        </div>
      ) : (
        <p className="cyber-muted text-sm">
          No open position. Strategy opens one when funding is positive.
        </p>
      )}
    </div>
  );
}

function Row({ label, value, valueClass = 'text-white' }: { label: string; value: string; valueClass?: string }) {
  return (
    <div className="flex justify-between">
      <span className="cyber-muted">{label}</span>
      <span className={valueClass}>{value}</span>
    </div>
  );
}
