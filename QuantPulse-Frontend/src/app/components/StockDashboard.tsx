import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Search, TrendingUp, AlertTriangle, Loader2, BarChart2 } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ||
    (window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "https://quantpulse-backend.onrender.com");

interface V2AnalysisResponse {
    ticker: string;
    regime: string;
    vix: number;
    ai_signal: string;
    confidence: string;
    final_report: string;
    details: {
        lstm: {
            probability: number;
            signal: string;
            features: Record<string, number>;
        };
        regime_detection: {
            regime: string;
            confidence: number;
            all_states: Record<string, unknown>;
        };
        war_room: {
            verdict: string;
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
            const response = await axios.get<V2AnalysisResponse>(
                `${API_BASE}/api/v2/analyze/${ticker.toUpperCase()}`
            );
            setData(response.data);
        } catch (err) {
            setError("Analysis failed. Please check backend connection or API limits.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
            {/* Search Header */}
            <div className="max-w-4xl mx-auto mb-12 text-center">
                <h1 className="text-5xl font-extrabold mb-4 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                    QuantPulse AI
                </h1>
                <p className="text-slate-400 mb-8">Agentic Hedge Fund Analysis Engine</p>

                <div className="flex gap-2 max-w-md mx-auto bg-slate-900 p-2 rounded-2xl border border-slate-800 shadow-2xl">
                    <input
                        type="text"
                        placeholder="Enter Ticker (e.g. RELIANCE)"
                        className="flex-1 bg-transparent border-none focus:ring-0 px-4 text-lg outline-none"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 p-3 rounded-xl transition-all cursor-pointer"
                    >
                        {loading ? <Loader2 className="animate-spin" /> : <Search />}
                    </button>
                </div>
            </div>

            {/* Main Analysis Area */}
            {data && (
                <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Quick Stats Sidebar */}
                    <div className="space-y-4">
                        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800">
                            <div className="flex items-center gap-3 text-slate-400 mb-2">
                                <BarChart2 size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">Regime</span>
                            </div>
                            <div className="text-2xl font-bold text-blue-400">{data.regime}</div>
                        </div>

                        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800">
                            <div className="flex items-center gap-3 text-slate-400 mb-2">
                                <TrendingUp size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">LSTM Signal</span>
                            </div>
                            <div className="text-2xl font-bold text-emerald-400">
                                {data.ai_signal} ({data.confidence})
                            </div>
                        </div>

                        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800">
                            <div className="flex items-center gap-3 text-slate-400 mb-2">
                                <AlertTriangle size={18} />
                                <span className="text-xs uppercase tracking-widest font-semibold">Market Volatility</span>
                            </div>
                            <div className="text-2xl font-bold text-yellow-500">VIX: {data.vix}</div>
                        </div>

                        {/* War Room Status */}
                        {data.details.war_room.error && (
                            <div className="bg-amber-900/20 p-4 rounded-2xl border border-amber-500/30">
                                <p className="text-xs text-amber-400 font-medium mb-1">⚠️ AI Agents Status</p>
                                <p className="text-xs text-amber-300/70">
                                    Agents temporarily offline. Showing LSTM + HMM analysis.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Detailed Investment Memo */}
                    <div className="lg:col-span-2 bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-2xl">
                        <div className="prose prose-invert max-w-none prose-headings:text-blue-400 prose-strong:text-emerald-400 prose-td:text-slate-300 prose-th:text-slate-400">
                            <ReactMarkdown>{data.final_report}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}

            {/* Error State */}
            {error && (
                <div className="max-w-md mx-auto mt-8 p-4 bg-red-900/20 border border-red-500/50 rounded-2xl text-red-400 text-center">
                    {error}
                </div>
            )}
        </div>
    );
};

export default StockDashboard;
