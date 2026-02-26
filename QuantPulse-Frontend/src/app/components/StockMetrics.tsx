import { Card } from '@/app/components/ui/card';
import { ArrowUp, ArrowDown, Activity, DollarSign } from 'lucide-react';

interface StockMetricsProps {
  currentPrice: number;
  change: number;
  changePercent: number;
  volume: string;
  marketCap: string;
}

export function StockMetrics({ currentPrice, change, changePercent, volume, marketCap }: StockMetricsProps) {
  const isPositive = change >= 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card variant="elevated" className="p-5 border-l-4 border-l-[#3A6FF8]">
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="size-4 text-zinc-400" />
          <p className="text-sm text-zinc-400 font-medium">Current Price</p>
        </div>
        <p className="text-2xl font-bold text-zinc-100">₹{currentPrice.toFixed(2)}</p>
        <div className={`flex items-center gap-1 mt-1 text-sm ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
          {isPositive ? <ArrowUp className="size-3" /> : <ArrowDown className="size-3" />}
          <span className="font-medium">₹{Math.abs(change).toFixed(2)} ({Math.abs(changePercent).toFixed(2)}%)</span>
        </div>
      </Card>

      <Card variant="default" className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <Activity className="size-4 text-zinc-400" />
          <p className="text-sm text-zinc-400">Day Change</p>
        </div>
        <p className={`text-2xl font-semibold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
          {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
        </p>
        <p className="text-xs text-zinc-500 mt-1 uppercase tracking-wide">
          {isPositive ? 'Gaining' : 'Losing'}
        </p>
      </Card>

      <Card variant="subtle" className="p-5">
        <div className="flex items-center gap-2 mb-2">
          <Activity className="size-4 text-zinc-400" />
          <p className="text-sm text-zinc-400">Volume</p>
        </div>
        <p className="text-2xl font-medium text-zinc-100">{volume}</p>
        <p className="text-sm text-zinc-500 mt-1">shares traded</p>
      </Card>

      <Card variant="flat" className="p-4 bg-[rgba(15,23,42,0.2)]">
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="size-4 text-zinc-400" />
          <p className="text-sm text-zinc-400">Market Cap</p>
        </div>
        <p className="text-2xl font-medium text-zinc-100">{marketCap}</p>
        <p className="text-sm text-zinc-500 mt-1">in crores</p>
      </Card>
    </div>
  );
}
