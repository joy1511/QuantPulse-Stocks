import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Search, TrendingUp, AlertTriangle, Loader2, BarChart2 } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ||
    (window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "https://quantpulse-stocks-backend.onrender.com");

interface V2AnalysisResponse {
    ticker: string;
    regime: string;
    vix: number;
    ai_outlook: string;
    confidence: string;
    final_report: string;
    details: {
        lstm: {
            probability: number;
            outlook: string;
            features: Record<string, number>;
        };
        regime_detection: {
            regime: string;
            confidence: number;
            all_states: Record<string, unknown>;
        };
        research_analysis: {
            technical_summary: string;
            agents_used: string[];
            error: string | null;
        };
    };
}

const StockDashboard = () => {
    const [ticker, setTicker] = useState("");
    const [data, setData] = useState<V2AnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async () => {
        if (!ticker) return;
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/v2/analyze/${ticker.toUpperCase()}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const json: V2AnalysisResponse = await response.json();
            setData(json);
        } catch (err) {
            setError("Analysis failed. Please check backend connection or API limits.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#121212] text-[#F0F0F0] p-8 font-sans">
            {/* Search Header */}
            <div className="max-w-4xl mx-auto mb-12 text-center">
                <h1 className="text-5xl font-extrabold mb-4 text-[#F0F0F0]">
                    QuantPulse AI
                </h1>
                <p className="text-[#A0A0A0] mb-8">AI-Powered Research Analysis Engine</p>

                <div className="flex gap-2 max-w-md mx-auto bg-[rgba(30, 30, 30, 0.9)] p-2 rounded-2xl border border-[#2A2A2A] shadow-2xl">
                    <input
                        type="text"
                        placeholder="Enter Ticker (e.g. RELIANCE)"
                        className="flex-1 bg-transparent border-none focus:ring-0 px-4 text-lg outline-none text-[#F0F0F0] placeholder:text-[#606060]"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-[#1A6FD4] hover:bg-[#2A7FE8] disabled:bg-[#2A2A2A] p-3 rounded-xl transition-all cursor-pointer"
                    >
                        {loading ? <Loader2 className="animate-spin text-white" /> : <Search className="text-white" />}
                    </button>
                </div>
            </div>

            {/* Main Analysis Area */}
            {data && (
                <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Quick Stats Sidebar */}
                    <div className="space-y-4">
                        <div className="bg-[rgba(30, 30, 30, 0.9)] p-6 rounded-2xl border border-[#2A2A2A]">
                            <div className="flex items-center gap-3 text-[#A0A0A0] mb-2">
                                <BarChart2 size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">Regime</span>
                            </div>
                            <div className="text-2xl font-bold text-[#4A9EFF]">{data.regime}</div>
                        </div>

                        <div className="bg-[rgba(30, 30, 30, 0.9)] p-6 rounded-2xl border border-[#2A2A2A]">
                            <div className="flex items-center gap-3 text-[#A0A0A0] mb-2">
                                <TrendingUp size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">LSTM Outlook</span>
                            </div>
                            <div className="text-2xl font-bold text-[#4CAF7D]">
                                {data.ai_outlook} ({data.confidence})
                            </div>
                        </div>

                        <div className="bg-[rgba(30, 30, 30, 0.9)] p-6 rounded-2xl border border-[#2A2A2A]">
                            <div className="flex items-center gap-3 text-[#A0A0A0] mb-2">
                                <AlertTriangle size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">Market Volatility</span>
                            </div>
                            <div className="text-2xl font-bold text-[#E8A838]">VIX: {data.vix}</div>
                        </div>

                        {/* Research Analysis Status */}
                        {data.details.research_analysis.error && (
                            <div className="bg-amber-500/5 p-4 rounded-2xl border border-[#E8A838]/20">
                                <p className="text-xs text-[#E8A838] font-medium mb-1">AI Agents Status</p>
                                <p className="text-xs text-[#A0A0A0]">
                                    Agents temporarily offline. Showing LSTM + HMM analysis.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Detailed Research Analysis Report */}
                    <div className="lg:col-span-2 bg-[rgba(30, 30, 30, 0.9)] p-8 rounded-2xl border border-[#2A2A2A] shadow-2xl">
                        <div className="prose prose-invert max-w-none prose-headings:text-[#4A9EFF] prose-strong:text-[#4CAF7D] prose-td:text-[#A0A0A0] prose-th:text-[#A0A0A0]">
                            <ReactMarkdown>{data.final_report}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}

            {/* Error State */}
            {error && (
                <div className="max-w-md mx-auto mt-8 p-4 bg-[#E05252]/10 border border-[#E05252]/20 rounded-2xl text-[#E05252] text-center">
                    {error}
                </div>
            )}
        </div>
    );
};

export default StockDashboard;
