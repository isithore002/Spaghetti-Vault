'use client';

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export function FundingChart({ points }: { points: Array<{ rate: number; ts: number }> }) {
  const data = points
    .slice()
    .reverse()
    .map((point, index) => ({ index, rate: Number((point.rate * 100).toFixed(5)) }));

  return (
    <div className="rounded-2xl border border-orange-400/25 bg-orange-500/5 p-6">
      <h3 className="font-cyber mb-4 text-sm text-orange-100">Funding Rate History</h3>
      {data.length ? (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data}>
            <XAxis dataKey="index" hide />
            <YAxis tickFormatter={(v) => `${v}%`} width={60} />
            <Tooltip formatter={(value: number) => [`${value}%`, 'Rate']} />
            <Line type="monotone" dataKey="rate" stroke="#ff8f2d" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p className="cyber-muted text-sm">Collecting funding-rate data...</p>
      )}
    </div>
  );
}
