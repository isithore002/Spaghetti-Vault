import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="cyber-shell min-h-screen px-5 py-10 md:px-10 md:py-14">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-7">
        <section className="cyber-panel relative overflow-hidden rounded-3xl p-8 md:p-12">
          <div className="absolute -left-16 top-10 h-40 w-40 rounded-full bg-orange-500/20 blur-2xl" />
          <div className="absolute -right-20 bottom-8 h-48 w-48 rounded-full bg-amber-300/15 blur-3xl" />

          <p className="cyber-title text-xs text-orange-300/90 md:text-sm">Pacifica Builder Vault</p>
          <h1 className="mt-3 max-w-4xl text-4xl font-extrabold leading-tight md:text-6xl">
            FluxVault // Funding Engine
          </h1>
          <p className="cyber-muted mt-4 max-w-2xl text-lg leading-relaxed">
            Deploy USDC. Authorize once. Harvest perp funding with automated short exposure and risk guardrails.
          </p>

          <div className="mt-7 grid gap-3 text-sm sm:grid-cols-3">
            <div className="cyber-kpi rounded-xl p-3">
              <p className="cyber-muted">Mode</p>
              <p className="text-xl font-bold text-orange-300">Carry Strategy</p>
            </div>
            <div className="cyber-kpi rounded-xl p-3">
              <p className="cyber-muted">Target Market</p>
              <p className="text-xl font-bold text-orange-300">SOL-PERP</p>
            </div>
            <div className="cyber-kpi rounded-xl p-3">
              <p className="cyber-muted">Activation</p>
              <p className="text-xl font-bold text-orange-300">Single Signature</p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/deposit"
              className="cyber-button rounded-xl px-6 py-3"
            >
              Enter Vault
            </Link>
            <Link
              href="/dashboard"
              className="rounded-xl border border-orange-400/45 px-6 py-3 font-semibold text-orange-100 transition hover:bg-orange-500/10"
            >
              Open Dashboard
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
