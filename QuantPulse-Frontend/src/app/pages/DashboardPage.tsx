import { useState, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { StockInput } from "@/app/components/StockInput";
import { StockChart } from "@/app/components/StockChart";
import { MarketContextStrip } from "@/app/components/MarketContextStrip";
import { MarketMovers } from "@/app/components/MarketMovers";
import {
  fetchStockData,
  fetchV2Analysis,
  type StockData,
  type V2AnalysisData,
} from "@/app/services/api";
import {
  Loader2,
  AlertCircle,
  Brain,
  TrendingUp,
  TrendingDown,
  BarChart2,
  AlertTriangle,
  FileText,
  Activity,
  Shield,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from "lucide-react";

// Chart data generator removed — real OHLC comes from V2 API response

export function DashboardPage() {
  const [selectedStock, setSelectedStock] = useState("RELIANCE");
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [v2Data, setV2Data] = useState<V2AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isV2Loading, setIsV2Loading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async (symbol: string) => {
    setIsLoading(true);
    setError(null);

    // 1. Fetch V1 stock data (for company name)
    try {
      const stock = await fetchStockData(symbol);
      setStockData(stock);
    } catch {
      setStockData(null);
    }
    setIsLoading(false);

    // 2. Fetch V2 AI Analysis — real OHLC + LSTM + HMM + War Room
    setIsV2Loading(true);
    try {
      const v2 = await fetchV2Analysis(symbol);
      setV2Data(v2);
    } catch (err) {
      console.warn("V2 Analysis failed:", err);
      setV2Data(null);
    } finally {
      setIsV2Loading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData(selectedStock);
  }, [selectedStock, loadDashboardData]);

  const handleSearch = (ticker: string) => {
    setSelectedStock(ticker.toUpperCase());
  };

  // Use V2 live price if available, fallback to V1
  const livePrice = v2Data?.stock_price?.current_price ?? stockData?.currentPrice ?? 0;
  const prevClose = v2Data?.stock_price?.previous_close ?? stockData?.previousClose ?? 0;
  const dayChange = v2Data?.stock_price?.day_change ?? stockData?.change ?? 0;
  const dayChangePct = v2Data?.stock_price?.day_change_pct ?? stockData?.changePercent ?? 0;
  const isPositive = dayChange >= 0;

  // Signal config
  const getOutlookConfig = (outlook: string) => {
    if (outlook.includes("Bullish")) {
      return { color: "text-[#4CAF7D]", bg: "bg-[#4CAF7D]/10", border: "border-[#4CAF7D]/20", icon: ArrowUpRight };
    } else if (outlook.includes("Bearish")) {
      return { color: "text-[#E05252]", bg: "bg-[#E05252]/10", border: "border-[#E05252]/20", icon: ArrowDownRight };
    } else {
      return { color: "text-[#4A9EFF]", bg: "bg-blue-500/10", border: "border-blue-500/20", icon: Minus };
    }
  };

  const getTechnicalSummaryConfig = (summary: string) => {
    if (summary.includes("Bullish")) return "bg-emerald-500/15 text-[#4CAF7D] border-[#4CAF7D]/20";
    if (summary.includes("Bearish")) return "bg-red-500/15 text-[#E05252] border-[#E05252]/20";
    return "bg-blue-500/15 text-[#4A9EFF] border-blue-500/30";
  };

  return (
    <div className="min-h-screen text-[#F0F0F0] p-6 relative">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none z-[-1]">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-900/10 rounded-full blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-[2rem] font-bold text-[#F0F0F0] mb-2 tracking-tight">
            Stock Analytics Dashboard
          </h1>
          <p className="text-[#A0A0A0] text-lg">
            Real-time NSE analysis powered by LSTM, HMM & AI Agents
          </p>
        </div>

        {/* Market Movers — Top Gainers + Losers */}
        <MarketMovers onStockClick={handleSearch} />

        {/* Stock Search */}
        <div className="relative z-10">
          <StockInput onSearch={handleSearch} disabled={isLoading || isV2Loading} />
        </div>

        {/* Market Context */}
        <MarketContextStrip />

        {/* Live Price Banner */}
        {(livePrice > 0) && (
          <div className="border-l-[6px] border-l-[#3A6FF8] bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-6 rounded-r-xl shadow-lg shadow-blue-900/5 flex items-center justify-between border-y border-r border-y-[#3A6FF8]/10 border-r-[#3A6FF8]/10">
            <div>
              <p className="text-sm text-[#A0A0A0] font-medium uppercase tracking-wider mb-1">
                Currently Viewing
              </p>
              <div className="flex items-baseline gap-3">
                <p className="text-3xl font-bold text-[#F0F0F0]">
                  {selectedStock}
                </p>
                <p className="text-sm text-[#A0A0A0] hidden md:block">
                  {stockData?.companyName || `${selectedStock}.NS`}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-[#F0F0F0]">
                ₹{livePrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </p>
              <p className={`text-sm font-medium flex items-center justify-end gap-1 ${isPositive ? "text-[#4CAF7D]" : "text-[#E05252]"}`}>
                {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                {isPositive ? "+" : ""}₹{dayChange.toFixed(2)} ({isPositive ? "+" : ""}{dayChangePct.toFixed(2)}%)
              </p>
            </div>
          </div>
        )}

        {/* Loading state */}
        {isLoading && !stockData && !v2Data ? (
          <div className="h-[400px] flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#2A2A2A] bg-[#1E1E1E]/20">
            <Loader2 className="size-8 text-[#4A9EFF] animate-spin mb-4" />
            <p className="text-[#A0A0A0]">Fetching live market data...</p>
          </div>
        ) : (
          <>
            {/* Chart — real OHLC from V2 */}
            {v2Data?.ohlc && v2Data.ohlc.length > 0 && (
              <StockChart ohlc={v2Data.ohlc} stockName={selectedStock} />
            )}

            {/* ============================================================== */}
            {/* AI ANALYSIS ENGINE — The Main Event */}
            {/* ============================================================== */}
            <div className="mt-4">
              <div className="flex items-center gap-3 mb-5">
                <div className="p-2 rounded-xl bg-[#1A6FD4]/10 border border-[#1A6FD4]/20">
                  <Brain className="size-5 text-[#4A9EFF]" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-[#F0F0F0]">AI Analysis Engine</h2>
                  <p className="text-xs text-[#A0A0A0]">LSTM Neural Network • HMM Regime Detection • Multi-Agent Debate</p>
                </div>
                {v2Data && (
                  <span className={`ml-auto text-sm font-bold px-4 py-1.5 rounded-full border ${getTechnicalSummaryConfig(v2Data.details.research_analysis.technical_summary)}`}>
                    {v2Data.details.research_analysis.technical_summary}
                  </span>
                )}
              </div>

              {isV2Loading ? (
                <div className="h-[250px] flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#2A2A2A] bg-[#1E1E1E]/20">
                  <Loader2 className="size-8 text-[#4A9EFF] animate-spin mb-4" />
                  <p className="text-[#A0A0A0] font-medium">Running AI Pipeline...</p>
                  <p className="text-[#606060] text-xs mt-1">LSTM → HMM → Agent Debate (~15-30s)</p>
                </div>
              ) : v2Data ? (
                <div className="space-y-5">
                  {/* Signal Cards Row */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* LSTM Outlook */}
                    {(() => {
                      const cfg = getOutlookConfig(v2Data.ai_outlook);
                      const Icon = cfg.icon;
                      return (
                        <div className={`${cfg.bg} border ${cfg.border} p-5 rounded-2xl`}>
                          <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                            <TrendingUp size={15} />
                            <span className="text-[10px] uppercase tracking-widest font-semibold">LSTM Outlook</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Icon size={20} className={cfg.color} />
                            <span className={`text-xl font-bold ${cfg.color}`}>{v2Data.ai_outlook}</span>
                          </div>
                          <p className="text-xs text-[#A0A0A0] mt-1">Probability: {v2Data.confidence}</p>
                        </div>
                      );
                    })()}

                    {/* Market Regime */}
                    <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A]">
                      <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                        <BarChart2 size={15} />
                        <span className="text-[10px] uppercase tracking-widest font-semibold">Regime (HMM)</span>
                      </div>
                      <p className={`text-xl font-bold ${v2Data.regime.includes("Bull") ? "text-[#4CAF7D]" :
                        v2Data.regime.includes("Bear") ? "text-[#E05252]" : "text-[#4A9EFF]"
                        }`}>{v2Data.regime}</p>
                      <p className="text-xs text-[#A0A0A0] mt-1">
                        Confidence: {(v2Data.details.regime_detection.confidence * 100).toFixed(0)}%
                      </p>
                    </div>

                    {/* India VIX */}
                    <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A]">
                      <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                        <Shield size={15} />
                        <span className="text-[10px] uppercase tracking-widest font-semibold">India VIX</span>
                      </div>
                      <p className={`text-xl font-bold ${v2Data.vix > 22 ? "text-[#E05252]" : v2Data.vix > 16 ? "text-[#E8A838]" : "text-[#4CAF7D]"}`}>
                        {v2Data.vix.toFixed(1)}
                      </p>
                      <p className="text-xs text-[#A0A0A0] mt-1">
                        {v2Data.vix > 22 ? "High fear" : v2Data.vix > 16 ? "Moderate" : "Calm"}
                      </p>
                    </div>

                    {/* Technical Snapshot */}
                    <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A]">
                      <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                        <Activity size={15} />
                        <span className="text-[10px] uppercase tracking-widest font-semibold">Technicals</span>
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="text-[#A0A0A0]">RSI</span>
                          <span className={`font-semibold ${v2Data.details.lstm.features.rsi > 70 ? "text-[#E05252]" :
                            v2Data.details.lstm.features.rsi < 30 ? "text-[#4CAF7D]" : "text-[#F0F0F0]"
                            }`}>{v2Data.details.lstm.features.rsi?.toFixed(1) ?? "—"}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#A0A0A0]">MACD</span>
                          <span className={`font-semibold ${v2Data.details.lstm.features.macd > 0 ? "text-[#4CAF7D]" : "text-[#E05252]"
                            }`}>{v2Data.details.lstm.features.macd?.toFixed(2) ?? "—"}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#A0A0A0]">Boll %B</span>
                          <span className="text-[#F0F0F0] font-semibold">{v2Data.details.lstm.features.bollinger_pctb?.toFixed(2) ?? "—"}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Agents Status (if offline) */}
                  {v2Data.details.research_analysis.error && (
                    <div className="flex items-center gap-3 bg-amber-500/5 border border-[#E8A838]/20 p-3 rounded-xl">
                      <AlertCircle className="size-4 text-[#E8A838] shrink-0" />
                      <p className="text-xs text-[#A0A0A0]">
                        AI agent analysis unavailable. Showing LSTM + HMM technical analysis.
                      </p>
                    </div>
                  )}

                  {/* Research Analysis Report */}
                  <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-6 lg:p-8 rounded-2xl border border-[#2A2A2A]">
                    <div className="flex items-center gap-2 mb-5">
                      <FileText size={16} className="text-[#4A9EFF]" />
                      <h3 className="text-sm font-semibold text-[#F0F0F0] uppercase tracking-wider">Research Analysis Report</h3>
                    </div>
                    <div className="prose prose-invert prose-sm max-w-none
                      prose-headings:text-[#4A9EFF] prose-headings:font-semibold prose-headings:mt-6 prose-headings:mb-3
                      prose-h2:text-lg prose-h3:text-base
                      prose-strong:text-[#4CAF7D]
                      prose-p:text-[#A0A0A0] prose-p:leading-relaxed
                      prose-li:text-[#A0A0A0]
                      prose-table:border-collapse prose-table:w-full
                      prose-th:bg-[#2A2A2A]/50 prose-th:text-[#A0A0A0] prose-th:text-left prose-th:px-4 prose-th:py-2 prose-th:text-xs prose-th:uppercase prose-th:tracking-wider prose-th:border prose-th:border-[#30363D]/50
                      prose-td:text-[#A0A0A0] prose-td:px-4 prose-td:py-2 prose-td:border prose-td:border-[#30363D]/30
                      prose-hr:border-[#30363D]/30
                    ">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{v2Data.final_report}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 rounded-2xl border border-dashed border-[#2A2A2A] bg-[#1E1E1E]/20 text-center">
                  <AlertCircle className="size-8 text-[#606060] mx-auto mb-3" />
                  <p className="text-[#A0A0A0] text-sm">V2 Analysis unavailable. Check backend connection.</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-[rgba(74, 158, 255, 0.15)]">
              <p className="text-center text-[10px] text-[#A0A0A0] uppercase tracking-widest">
                QuantPulse India • AI-Powered Research Analytics • {new Date().getFullYear()}
              </p>
              <p className="text-center text-[9px] text-[#606060] mt-1">
                Research data for educational purposes. Stocks are inherently unpredictable.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
