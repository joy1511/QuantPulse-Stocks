import { Card } from '@/app/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SentimentIndicatorProps {
  sentiment: 'positive' | 'neutral' | 'negative';
}

export function SentimentIndicator({ sentiment }: SentimentIndicatorProps) {
  const getSentimentConfig = () => {
    switch (sentiment) {
      case 'positive':
        return {
          icon: TrendingUp,
          label: 'Positive',
          color: 'text-[#4CAF7D]',
          bgColor: 'bg-[#4CAF7D]/10',
          borderColor: 'border-[#4CAF7D]/20'
        };
      case 'negative':
        return {
          icon: TrendingDown,
          label: 'Negative',
          color: 'text-[#E05252]',
          bgColor: 'bg-[#E05252]/10',
          borderColor: 'border-[#E05252]/20'
        };
      case 'neutral':
        return {
          icon: Minus,
          label: 'Neutral',
          color: 'text-[#E8A838]',
          bgColor: 'bg-[#E8A838]/10',
          borderColor: 'border-[#E8A838]/20'
        };
    }
  };

  const config = getSentimentConfig();
  const Icon = config.icon;

  return (
    <Card variant="subtle" className={`p-6 ${config.borderColor} border`}>
      <div className="flex items-center gap-3">
        <div className={`p-3 rounded-lg ${config.bgColor}`}>
          <Icon className={`size-6 ${config.color}`} />
        </div>
        <div>
          <p className="text-sm text-[#A0A0A0]">Market Sentiment</p>
          <p className={`text-xl ${config.color}`}>{config.label}</p>
        </div>
      </div>
    </Card>
  );
}
