import { Card } from '@/app/components/ui/card';
import { ArrowUp, ArrowDown, ArrowRight, TrendingUp, HelpCircle, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { Progress } from '@/app/components/ui/progress';
import { useState } from 'react';
import type { AIPredictionData } from '@/app/services/api';

interface AIPredictionCardProps {
  data: AIPredictionData | null;
  isLoading?: boolean;
  error?: string | null;
}

export function AIPredictionCard({ data, isLoading = false, error = null }: AIPredictionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getPredictionConfig = (direction: string) => {
    switch (direction) {
      case 'UP':
        return {
          icon: ArrowUp,
          label: 'UP',
          description: 'Bullish Trend',
          color: 'text-[#4CAF7D]',
          bgColor: 'bg-emerald-500/15',
          borderColor: 'border-[#4CAF7D]/20'
        };
      case 'DOWN':
        return {
          icon: ArrowDown,
          label: 'DOWN',
          description: 'Bearish Trend',
          color: 'text-[#E05252]',
          bgColor: 'bg-red-500/15',
          borderColor: 'border-[#E05252]/20'
        };
      default:
        return {
          icon: ArrowRight,
          label: 'SIDEWAYS',
          description: 'Consolidation',
          color: 'text-[#4A9EFF]',
          bgColor: 'bg-blue-500/15',
          borderColor: 'border-blue-500/40'
        };
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Card variant="elevated" className="p-6 border-l-[6px] border-blue-500/40">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="size-5 text-[#4A9EFF]" />
          <h3 className="text-lg text-[#F0F0F0]">AI Prediction</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="size-8 text-[#4A9EFF] animate-spin" />
        </div>
        <p className="text-xs text-[#A0A0A0] text-center">Analyzing market data...</p>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card variant="elevated" className="p-6 border-l-[6px] border-[#E05252]/20">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="size-5 text-[#4A9EFF]" />
          <h3 className="text-lg text-[#F0F0F0]">AI Prediction</h3>
        </div>
        <p className="text-sm text-[#E05252]/80">{error}</p>
      </Card>
    );
  }

  // No data state
  if (!data) {
    return (
      <Card variant="elevated" className="p-6 border-l-[6px] border-zinc-500/40">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="size-5 text-[#4A9EFF]" />
          <h3 className="text-lg text-[#F0F0F0]">AI Prediction</h3>
        </div>
        <p className="text-sm text-[#A0A0A0]">Select a stock to see prediction</p>
      </Card>
    );
  }

  const config = getPredictionConfig(data.prediction.direction);
  const Icon = config.icon;

  return (
    <Card variant="elevated" className={`p-6 border-l-[6px] ${config.borderColor} shadow-lg shadow-black/10`}>
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="size-5 text-[#4A9EFF]" />
        <h3 className="text-lg text-[#F0F0F0]">AI Prediction</h3>
      </div>

      {/* Direction & Trend */}
      <div className="flex items-center gap-4 mb-6">
        <div className={`p-4 rounded-xl ${config.bgColor}`}>
          <Icon className={`size-8 ${config.color}`} />
        </div>
        <div>
          <p className={`text-3xl font-semibold ${config.color}`}>{config.label}</p>
          <p className="text-sm text-[#A0A0A0]">{data.prediction.trendLabel}</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Overall Confidence */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#A0A0A0] font-medium">Overall Confidence</span>
            <span className="text-lg text-[#F0F0F0] font-bold">{data.prediction.overallConfidence}%</span>
          </div>
          <Progress value={data.prediction.overallConfidence} className="h-2" />
        </div>

        {/* Confidence Decomposition */}
        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-[rgba(74, 158, 255, 0.15)]">
          {/* Technical Confidence */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-[#A0A0A0]">Technical</span>
              <span className="text-[#A0A0A0]">{data.technical.confidence}%</span>
            </div>
            <Progress value={data.technical.confidence} className="h-1.5 opacity-70" />
            <span className="text-[10px] text-[#606060]">{data.technical.weight} weight</span>
          </div>
          {/* News Confidence */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-[#A0A0A0]">News</span>
              <span className="text-[#A0A0A0]">{data.news.confidence}%</span>
            </div>
            <Progress value={data.news.confidence} className="h-1.5 opacity-70" />
            <span className="text-[10px] text-[#606060]">{data.news.weight} weight</span>
          </div>
        </div>

        {/* Signal Agreement Indicator */}
        <div className="flex items-center gap-2 mt-2">
          <div className={`size-2 rounded-full ${data.prediction.signalsAgree ? 'bg-emerald-500' : data.prediction.signalsConflict ? 'bg-amber-500' : 'bg-blue-400'}`} />
          <span className="text-xs text-[#A0A0A0]">
            {data.prediction.signalsAgree
              ? 'Technical & News signals agree'
              : data.prediction.signalsConflict
                ? 'Signals conflict – using technical direction'
                : 'News signal is neutral'}
          </span>
        </div>
      </div>

      {/* AI Explainability Section - Using backend explanations only */}
      <div className="mt-6 pt-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-xs text-[#A0A0A0] hover:text-[#4A9EFF] transition-colors group"
        >
          <span className="flex items-center gap-1.5">
            <HelpCircle className="size-3.5" />
            Why this prediction?
          </span>
          {isExpanded ? <ChevronUp className="size-3.5" /> : <ChevronDown className="size-3.5" />}
        </button>

        {isExpanded && (
          <div className="mt-3 p-3 bg-[#1E1E1E]/30 rounded-lg border border-[#30363D]/40">
            <ul className="space-y-2 text-xs text-[#A0A0A0]">
              {data.explanation.map((line, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-[#4A9EFF] mt-0.5 shrink-0">•</span>
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Footer with disclaimer */}
      <div className="mt-4 pt-4 border-t border-[rgba(74, 158, 255, 0.15)]">
        <p className="text-[10px] text-[#A0A0A0] leading-relaxed">
          {data.disclaimer}
        </p>
      </div>
    </Card>
  );
}
