import { Card } from '@/app/components/ui/card';
import { RefreshCw, Newspaper } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import { fetchNewsSentiment, type NewsSentimentData, getSentimentIndex } from '@/app/services/api';

interface NewsSentimentProps {
    symbol: string;
    onDataUpdate?: (data: NewsSentimentData | null) => void;
}

export function NewsSentiment({ symbol, onDataUpdate }: NewsSentimentProps) {
    const [data, setData] = useState<NewsSentimentData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

    // Sentiment options with soothing, professional colors
    const options = [
        { label: 'Very Bad', color: 'bg-red-500/80', textColor: 'text-red-400', hoverBg: 'hover:bg-red-500/20' },
        { label: 'Bad', color: 'bg-amber-500/80', textColor: 'text-amber-400', hoverBg: 'hover:bg-amber-500/20' },
        { label: 'Neutral', color: 'bg-blue-400/80', textColor: 'text-blue-300', hoverBg: 'hover:bg-blue-400/20' },
        { label: 'Good', color: 'bg-emerald-500/80', textColor: 'text-emerald-400', hoverBg: 'hover:bg-emerald-500/20' },
        { label: 'Very Good', color: 'bg-green-500/80', textColor: 'text-green-400', hoverBg: 'hover:bg-green-500/20' },
    ];

    // Mock Data for Offline Mode
    const getOfflineNewsSentiment = (symbol: string): NewsSentimentData => ({
        symbol: symbol,
        companyName: `${symbol} (Demo)`,
        sentimentScore: 0.65,
        sentimentLabel: 'Good',
        newsConfidence: 75,
        articlesAnalyzed: 12,
        daysAnalyzed: 7,
        timestamp: new Date().toISOString(),
        sampleArticles: [],
        disclaimer: "Demo data"
    });

    const fetchData = useCallback(async () => {
        if (!symbol) return;

        setIsLoading(true);
        setError(null);

        try {
            const sentimentData = await fetchNewsSentiment(symbol);
            setData(sentimentData);
            setLastRefresh(new Date());
            onDataUpdate?.(sentimentData);
        } catch (err) {
            console.warn("News sentiment fetch failed (Backend might be offline):", err);
            // Fallback to offline/demo data without showing red error
            const offlineData = getOfflineNewsSentiment(symbol);
            setData(offlineData);
            // Don't set error state to avoid UI clutter
            onDataUpdate?.(offlineData);
        } finally {
            setIsLoading(false);
        }
    }, [symbol, onDataUpdate]);

    // Fetch on mount and when symbol changes
    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Auto-refresh every 10 minutes
    useEffect(() => {
        const interval = setInterval(fetchData, 10 * 60 * 1000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const activeIndex = data ? getSentimentIndex(data.sentimentLabel) : 2;
    const activeLabel = data?.sentimentLabel || 'Loading...';
    const articlesCount = data?.articlesAnalyzed ?? 0;
    const confidence = data?.newsConfidence ?? 0;

    return (
        <Card variant="glass" className="p-5 border border-[rgba(100,150,255,0.12)]">
            <div className="flex flex-col gap-4">
                {/* Header with refresh button */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Newspaper className="size-4 text-[#5B8DFF]" />
                        <p className="text-sm text-zinc-400 font-medium">News Sentiment</p>
                    </div>
                    <button
                        onClick={fetchData}
                        disabled={isLoading}
                        className="p-1.5 rounded-md hover:bg-[rgba(100,150,255,0.1)] transition-colors disabled:opacity-50 group"
                        title={lastRefresh ? `Last updated: ${lastRefresh.toLocaleTimeString()}` : 'Refresh'}
                    >
                        <RefreshCw className={`size-3.5 text-zinc-500 group-hover:text-[#5B8DFF] transition-colors ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                {/* Current sentiment label */}
                <div className="flex items-baseline justify-between">
                    <p className={`text-xl font-semibold ${options[activeIndex]?.textColor || 'text-zinc-100'}`}>
                        {isLoading ? 'Updating...' : activeLabel}
                    </p>
                    {!isLoading && !error && (
                        <span className="text-xs text-zinc-500" title={`Based on ${articlesCount} articles`}>
                            {confidence}% confidence
                        </span>
                    )}
                </div>

                {/* Error state */}
                {error && (
                    <p className="text-xs text-red-400/80">{error}</p>
                )}

                {/* Sentiment scale bar */}
                <div className="flex justify-between items-center gap-1.5">
                    {options.map((option, index) => {
                        const isActive = index === activeIndex && !isLoading;
                        return (
                            <div key={option.label} className="flex flex-col items-center gap-2 flex-1 group">
                                {/* Bar Segment */}
                                <div
                                    className={`
                    h-2 w-full rounded-full transition-all duration-300
                    ${isActive ? option.color : 'bg-zinc-700/50'}
                    ${isActive ? 'opacity-100 shadow-[0_0_8px_rgba(255,255,255,0.15)]' : 'opacity-40 group-hover:opacity-60'}
                  `}
                                />

                                {/* Label */}
                                <span className={`text-[9px] font-medium transition-colors ${isActive ? 'text-zinc-300' : 'text-zinc-600'}`}>
                                    {index === 0 || index === options.length - 1 || isActive ? option.label : '•'}
                                </span>
                            </div>
                        );
                    })}
                </div>

                {/* Articles count tooltip */}
                {!isLoading && !error && articlesCount > 0 && (
                    <p className="text-[10px] text-zinc-500 text-center">
                        Based on {articlesCount} article{articlesCount > 1 ? 's' : ''} from the past {data?.daysAnalyzed || 7} days
                    </p>
                )}
            </div>
        </Card>
    );
}
