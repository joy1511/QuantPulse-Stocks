import { useState } from 'react';
import { Input } from '@/app/components/ui/input';
import { Button } from '@/app/components/ui/button';
import { Search, TrendingUp } from 'lucide-react';

interface StockInputProps {
  onSearch: (ticker: string) => void;
  disabled?: boolean;
}

export function StockInput({ onSearch, disabled }: StockInputProps) {
  const [ticker, setTicker] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) {
      onSearch(ticker.toUpperCase());
    }
  };

  const popularStocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'];

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-[#A0A0A0]" />
          <Input
            type="text"
            placeholder="Enter NSE stock ticker (e.g., RELIANCE, TCS)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            disabled={disabled}
            className="pl-10"
          />
        </div>
        <Button type="submit" disabled={disabled || !ticker.trim()}>
          <TrendingUp className="size-4 mr-2" />
          Analyze
        </Button>
      </form>

      <div className="flex items-center gap-2">
        <span className="text-sm text-[#A0A0A0]">Popular:</span>
        {popularStocks.map((stock) => (
          <button
            key={stock}
            onClick={() => {
              setTicker(stock);
              onSearch(stock);
            }}
            disabled={disabled}
            className="px-3 py-1 text-sm rounded-md bg-[rgba(30, 30, 30, 0.9)] hover:bg-[rgba(74,158,255,0.15)] border border-[rgba(74, 158, 255, 0.15)] text-[#A0A0A0] transition-colors backdrop-blur-sm disabled:opacity-50 disabled:pointer-events-none"
          >
            {stock}
          </button>
        ))}
      </div>
    </div>
  );
}
