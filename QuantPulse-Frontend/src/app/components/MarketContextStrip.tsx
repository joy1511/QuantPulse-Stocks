import { useEffect, useState } from 'react';
import { Zap, Activity, BarChart2 } from 'lucide-react';
import { Card } from '@/app/components/ui/card';

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://quantpulse-stocks-backend.onrender.com");

interface MarketContext {
  regime: string;
  vix: number;
}

export function MarketContextStrip() {
  const [ctx, setCtx] = useState<MarketContext | null>(null);

  useEffect(() => {
    // Fetch a lightweight analysis for NIFTY to get live regime + VIX
    fetch(`${API_BASE}/api/v2/analyze/NIFTY50`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.regime && data?.vix != null) {
          setCtx({ regime: data.regime, vix: data.vix });
        }
      })
      .catch(() => {/* silently fail — strip stays static */});
  }, []);

  const regime = ctx?.regime ?? "Loading...";
  const vix = ctx?.vix;

  const regimeColor = regime.includes("Bull")
    ? "text-emerald-500 bg-emerald-500/10"
    : regime.includes("Bear")
    ? "text-red-400 bg-red-500/10"
    : "text-blue-400 bg-blue-500/10";

  const vixLabel = vix == null
    ? "—"
    : vix > 22 ? "High" : vix > 16 ? "Medium" : "Low";
  const vixColor = vix == null
    ? "text-zinc-400 bg-zinc-500/10"
    : vix > 22
    ? "text-red-400 bg-red-500/10"
    : vix > 16
    ? "text-amber-500 bg-amber-500/10"
    : "text-emerald-500 bg-emerald-500/10";

  return (
    <Card variant="subtle" className="p-3 mb-6 bg-[rgba(15,23,42,0.4)] border-none">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2">
          <Activity className="size-4 text-zinc-500" />
          <span className="text-zinc-500 font-medium">Market Regime:</span>
          <span className={`font-semibold px-2 py-0.5 rounded ${regimeColor}`}>
            {regime}
          </span>
        </div>

        <div className="w-px h-4 bg-zinc-800 hidden sm:block" />

        <div className="flex items-center gap-2">
          <BarChart2 className="size-4 text-zinc-500" />
          <span className="text-zinc-500 font-medium">India VIX:</span>
          <span className={`font-semibold px-2 py-0.5 rounded ${vixColor}`}>
            {vix != null ? `${vix.toFixed(1)} — ${vixLabel}` : "—"}
          </span>
        </div>

        <div className="w-px h-4 bg-zinc-800 hidden sm:block" />

        <div className="flex items-center gap-2">
          <Zap className="size-4 text-zinc-500" />
          <span className="text-zinc-500 font-medium">Volatility:</span>
          <span className={`font-semibold px-2 py-0.5 rounded ${vixColor}`}>
            {vixLabel}
          </span>
        </div>
      </div>
    </Card>
  );
}
