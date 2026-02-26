import { Zap, Activity, BarChart2 } from 'lucide-react';
import { Card } from '@/app/components/ui/card';

export function MarketContextStrip() {
    return (
        <Card variant="subtle" className="p-3 mb-6 bg-[rgba(15,23,42,0.4)] border-none">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
                <div className="flex items-center gap-2">
                    <Activity className="size-4 text-zinc-500" />
                    <span className="text-zinc-500 font-medium">Market Index:</span>
                    <span className="text-emerald-500 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded">NIFTY: Bullish</span>
                </div>

                <div className="w-px h-4 bg-zinc-800 hidden sm:block"></div>

                <div className="flex items-center gap-2">
                    <BarChart2 className="size-4 text-zinc-500" />
                    <span className="text-zinc-500 font-medium">Sector Trend:</span>
                    <span className="text-blue-400 font-semibold bg-blue-500/10 px-2 py-0.5 rounded">Energy: Neutral</span>
                </div>

                <div className="w-px h-4 bg-zinc-800 hidden sm:block"></div>

                <div className="flex items-center gap-2">
                    <Zap className="size-4 text-zinc-500" />
                    <span className="text-zinc-500 font-medium">Volatility:</span>
                    <span className="text-amber-500 font-semibold bg-amber-500/10 px-2 py-0.5 rounded">Medium</span>
                </div>
            </div>
        </Card>
    );
}
