import { useState, useEffect } from "react";
import { fetchTrendingStocks, type TrendingStock } from "@/app/services/api";
import {
    TrendingUp,
    TrendingDown,
    ArrowUpRight,
    ArrowDownRight,
    Loader2,
    Flame,
} from "lucide-react";

// Map company names → NSE ticker symbols (Nifty 50)
const COMPANY_TO_TICKER: Record<string, string> = {
    "JSW Steel": "JSWSTEEL",
    "Tech Mahindra": "TECHM",
    "Tata Steel": "TATASTEEL",
    "Coal India": "COALINDIA",
    "Infosys": "INFY",
    "Hindalco Industries": "HINDALCO",
    "HDFC Bank": "HDFCBANK",
    "HDFC Life Insurance Company": "HDFCLIFE",
    "Oil and Natural Gas Corporation": "ONGC",
    "Shriram Finance": "SHRIRAMFIN",
    "Reliance Industries": "RELIANCE",
    "Tata Consultancy Services": "TCS",
    "ICICI Bank": "ICICIBANK",
    "Bharti Airtel": "BHARTIARTL",
    "State Bank of India": "SBIN",
    "Kotak Mahindra Bank": "KOTAKBANK",
    "Larsen & Toubro": "LT",
    "ITC": "ITC",
    "Axis Bank": "AXISBANK",
    "Bajaj Finance": "BAJFINANCE",
    "Wipro": "WIPRO",
    "HCL Technologies": "HCLTECH",
    "Maruti Suzuki India": "MARUTI",
    "Sun Pharmaceutical Industries": "SUNPHARMA",
    "Titan Company": "TITAN",
    "Adani Ports and Special Economic Zone": "ADANIPORTS",
    "Adani Enterprises": "ADANIENT",
    "Mahindra & Mahindra": "M&M",
    "Tata Motors": "TATAMOTORS",
    "Power Grid Corporation of India": "POWERGRID",
    "NTPC": "NTPC",
    "Asian Paints": "ASIANPAINT",
    "UltraTech Cement": "ULTRACEMCO",
    "Bajaj Finserv": "BAJAJFINSV",
    "Nestle India": "NESTLEIND",
    "IndusInd Bank": "INDUSINDBK",
    "Cipla": "CIPLA",
    "Dr. Reddy's Laboratories": "DRREDDY",
    "Grasim Industries": "GRASIM",
    "Britannia Industries": "BRITANNIA",
    "Eicher Motors": "EICHERMOT",
    "Tata Consumer Products": "TATACONSUM",
    "Apollo Hospitals Enterprise": "APOLLOHOSP",
    "Hero MotoCorp": "HEROMOTOCO",
    "Divi's Laboratories": "DIVISLAB",
    "SBI Life Insurance Company": "SBILIFE",
    "Bharat Petroleum Corporation": "BPCL",
    "Bharat Electronics": "BEL",
    "Hindustan Unilever": "HINDUNILVR",
};

function resolveTicker(stock: TrendingStock): string {
    if (COMPANY_TO_TICKER[stock.company]) {
        return COMPANY_TO_TICKER[stock.company];
    }
    // Fallback: strip suffixes and uppercase
    return stock.company
        .replace(/ Ltd\.?$/i, "")
        .replace(/ Limited$/i, "")
        .replace(/ Industries$/i, "")
        .replace(/ Corporation$/i, "")
        .trim()
        .toUpperCase()
        .replace(/\s+/g, "");
}

interface MarketMoversProps {
    onStockClick?: (ticker: string) => void;
}

export function MarketMovers({ onStockClick }: MarketMoversProps) {
    const [gainers, setGainers] = useState<TrendingStock[]>([]);
    const [losers, setLosers] = useState<TrendingStock[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;

        async function load() {
            try {
                const data = await fetchTrendingStocks();
                if (!cancelled) {
                    setGainers(data.top_gainers);
                    setLosers(data.top_losers);
                    setError(null);
                }
            } catch {
                if (!cancelled) setError("Market data unavailable");
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        }

        load();
        const interval = setInterval(load, 180_000);
        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, []);

    const handleClick = (stock: TrendingStock) => {
        onStockClick?.(resolveTicker(stock));
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-24 rounded-2xl border border-white/5 bg-[rgba(15,23,42,0.3)]">
                <Loader2 className="size-5 text-zinc-500 animate-spin" />
                <span className="ml-2 text-xs text-zinc-500">Loading market movers…</span>
            </div>
        );
    }

    if (error || (gainers.length === 0 && losers.length === 0)) {
        return null;
    }

    return (
        <div className="space-y-4">
            {/* Section header */}
            <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <Flame className="size-4 text-amber-400" />
                </div>
                <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
                    Today's Market Movers
                </h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* ── Top Gainers ───────────────────────────────────────── */}
                <div className="rounded-2xl bg-[rgba(15,23,42,0.4)] backdrop-blur-xl border border-emerald-500/10 p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="size-4 text-emerald-400" />
                        <span className="text-[11px] text-emerald-400 font-semibold uppercase tracking-widest">
                            Top Gainers
                        </span>
                    </div>

                    <div className="space-y-1">
                        {gainers.map((stock, i) => (
                            <button
                                key={stock.ticker || i}
                                onClick={() => handleClick(stock)}
                                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-emerald-500/5 transition-all group text-left"
                            >
                                <div className="flex items-center gap-3 min-w-0">
                                    <span className="text-[10px] text-zinc-600 font-mono w-4 shrink-0">
                                        {i + 1}
                                    </span>
                                    <div className="min-w-0">
                                        <p className="text-sm font-semibold text-zinc-200 group-hover:text-emerald-300 transition-colors truncate">
                                            {stock.company}
                                        </p>
                                        <p className="text-[10px] text-zinc-500 font-mono">
                                            {resolveTicker(stock)}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right shrink-0 ml-2">
                                    <p className="text-sm font-semibold text-zinc-200">
                                        ₹{stock.price.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </p>
                                    <p className="text-[11px] font-medium text-emerald-400 flex items-center justify-end gap-0.5">
                                        <ArrowUpRight size={11} />
                                        +{stock.percent_change.toFixed(2)}%
                                    </p>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* ── Top Losers ────────────────────────────────────────── */}
                <div className="rounded-2xl bg-[rgba(15,23,42,0.4)] backdrop-blur-xl border border-red-500/10 p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingDown className="size-4 text-red-400" />
                        <span className="text-[11px] text-red-400 font-semibold uppercase tracking-widest">
                            Top Losers
                        </span>
                    </div>

                    <div className="space-y-1">
                        {losers.map((stock, i) => (
                            <button
                                key={stock.ticker || i}
                                onClick={() => handleClick(stock)}
                                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-red-500/5 transition-all group text-left"
                            >
                                <div className="flex items-center gap-3 min-w-0">
                                    <span className="text-[10px] text-zinc-600 font-mono w-4 shrink-0">
                                        {i + 1}
                                    </span>
                                    <div className="min-w-0">
                                        <p className="text-sm font-semibold text-zinc-200 group-hover:text-red-300 transition-colors truncate">
                                            {stock.company}
                                        </p>
                                        <p className="text-[10px] text-zinc-500 font-mono">
                                            {resolveTicker(stock)}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right shrink-0 ml-2">
                                    <p className="text-sm font-semibold text-zinc-200">
                                        ₹{stock.price.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </p>
                                    <p className="text-[11px] font-medium text-red-400 flex items-center justify-end gap-0.5">
                                        <ArrowDownRight size={11} />
                                        {stock.percent_change.toFixed(2)}%
                                    </p>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
