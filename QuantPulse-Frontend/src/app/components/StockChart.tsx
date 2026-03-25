import { useState, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { Card } from '@/app/components/ui/card';

interface OHLCPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockChartProps {
  ohlc: OHLCPoint[];
  stockName: string;
}

const RANGES = [
  { label: '1W', days: 7 },
  { label: '1M', days: 30 },
  { label: '3M', days: 90 },
];

export function StockChart({ ohlc, stockName }: StockChartProps) {
  const [range, setRange] = useState('1M');

  const data = useMemo(() => {
    const days = RANGES.find(r => r.label === range)?.days ?? 30;
    return ohlc.slice(-days).map(p => ({
      date: p.date,
      close: p.close,
      // short label for x-axis
      label: new Date(p.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    }));
  }, [ohlc, range]);

  const firstClose = data[0]?.close ?? 0;
  const lastClose = data[data.length - 1]?.close ?? 0;
  const isPositive = lastClose >= firstClose;
  const lineColor = isPositive ? '#10b981' : '#ef4444';

  const minClose = Math.min(...data.map(d => d.close));
  const maxClose = Math.max(...data.map(d => d.close));
  const padding = (maxClose - minClose) * 0.05;

  if (!ohlc || ohlc.length === 0) return null;

  return (
    <Card variant="subtle" className="p-6 pb-4">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-base font-semibold text-[#F0F0F0]">{stockName} — Price History</h3>
          <p className="text-xs text-[#A0A0A0] mt-0.5">Daily closing price · NSE</p>
        </div>
        <div className="flex bg-[#1E1E1E]/60 rounded-lg p-0.5 border border-[#2A2A2A]">
          {RANGES.map(r => (
            <button
              key={r.label}
              onClick={() => setRange(r.label)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                range === r.label
                  ? 'bg-[#2A2A2A] text-[#F0F0F0] shadow-sm'
                  : 'text-[#A0A0A0] hover:text-[#A0A0A0]'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(74, 158, 255, 0.15)" vertical={false} />
          <XAxis
            dataKey="label"
            stroke="#2A2A2A"
            tick={{ fill: '#606060', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#2A2A2A"
            tick={{ fill: '#606060', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `₹${v.toLocaleString('en-IN')}`}
            domain={[minClose - padding, maxClose + padding]}
            width={72}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(30, 30, 30, 0.9)',
              border: '1px solid rgba(74, 158, 255, 0.15)',
              borderRadius: '10px',
              color: '#F0F0F0',
              fontSize: '12px',
            }}
            labelStyle={{ color: '#606060', marginBottom: '4px' }}
            formatter={(value: number) => [`₹${value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Close']}
          />
          <ReferenceLine y={firstClose} stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="close"
            stroke={lineColor}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5, strokeWidth: 0, fill: '#fff' }}
            animationDuration={800}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
