import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '@/app/components/ui/card';

interface StockChartProps {
  data: Array<{ time: string; price: number }>;
  stockName: string;
}

export function StockChart({ data, stockName }: StockChartProps) {
  const [timeRange, setTimeRange] = useState('1D');

  return (
    <Card variant="subtle" className="p-7 pb-8 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-2 opacity-50 pointer-events-none">
        <span className="text-[10px] uppercase tracking-widest text-[#5B8DFF]/40 font-bold border border-[#5B8DFF]/10 px-2 py-0.5 rounded">
          Demonstration Mode
        </span>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex flex-col">
          <h3 className="text-lg text-zinc-100">Price Movement - {stockName}</h3>
          <p className="text-xs text-zinc-500">Intraday price trend (Simulated)</p>
        </div>
        <div className="flex bg-zinc-900/50 rounded-lg p-0.5 border border-zinc-800">
          {['1D', '1W', '1M'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`
                px-3 py-1 text-xs font-medium rounded-md transition-all
                ${timeRange === range
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-500 hover:text-zinc-300'}
              `}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,150,255,0.05)" vertical={false} />
          <XAxis
            dataKey="time"
            stroke="#52525b"
            style={{ fontSize: '10px' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#52525b"
            style={{ fontSize: '10px' }}
            domain={['auto', 'auto']}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `₹${value}`}
            width={40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(100, 150, 255, 0.2)',
              borderRadius: '8px',
              color: '#fafafa',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
            }}
            labelStyle={{ color: '#71717a', fontSize: '11px', marginBottom: '4px' }}
          />
          <defs>
            <linearGradient id="lineColor" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#3A6FF8" />
              <stop offset="100%" stopColor="#60A5FA" />
            </linearGradient>
          </defs>
          <Line
            type="natural"
            dataKey="price"
            stroke="url(#lineColor)"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, strokeWidth: 0, fill: '#fff' }}
            animationDuration={1500}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
