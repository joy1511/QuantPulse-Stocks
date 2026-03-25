import { useState, useEffect, useCallback } from "react";
import {
    getHoldings,
    addHolding,
    updateHolding,
    deleteHolding,
    type PortfolioHolding,
    type EnrichedHolding,
} from "@/app/services/portfolioStore";
import { fetchStockData } from "@/app/services/api";
import {
    Briefcase,
    Plus,
    Pencil,
    Trash2,
    Loader2,
    TrendingUp,
    TrendingDown,
    IndianRupee,
    BarChart3,
    ArrowUpRight,
    ArrowDownRight,
    X,
    RefreshCw,
} from "lucide-react";

// ── Add / Edit Modal ─────────────────────────────────────────────────

interface HoldingFormData {
    symbol: string;
    buyPrice: string;
    quantity: string;
    buyDate: string;
    notes: string;
}

const emptyForm: HoldingFormData = {
    symbol: "",
    buyPrice: "",
    quantity: "",
    buyDate: new Date().toISOString().slice(0, 10),
    notes: "",
};

function HoldingModal({
    isOpen,
    onClose,
    onSave,
    editingHolding,
}: {
    isOpen: boolean;
    onClose: () => void;
    onSave: (data: HoldingFormData) => void;
    editingHolding: PortfolioHolding | null;
}) {
    const [form, setForm] = useState<HoldingFormData>(emptyForm);

    useEffect(() => {
        if (editingHolding) {
            setForm({
                symbol: editingHolding.symbol,
                buyPrice: editingHolding.buyPrice.toString(),
                quantity: editingHolding.quantity.toString(),
                buyDate: editingHolding.buyDate,
                notes: editingHolding.notes,
            });
        } else {
            setForm(emptyForm);
        }
    }, [editingHolding, isOpen]);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.symbol || !form.buyPrice || !form.quantity) return;
        onSave(form);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-[#121212]/80 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-md mx-4 bg-[rgba(30, 30, 30, 0.9)] border border-[#2A2A2A] rounded-2xl shadow-2xl shadow-black/50 p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-[#F0F0F0]">
                        {editingHolding ? "Edit Holding" : "Add Stock Holding"}
                    </h3>
                    <button
                        onClick={onClose}
                        className="p-1.5 rounded-lg hover:bg-white/5 text-[#A0A0A0] hover:text-[#F0F0F0] transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Symbol */}
                    <div>
                        <label className="block text-xs font-medium text-[#A0A0A0] mb-1.5 uppercase tracking-wider">
                            Stock Symbol *
                        </label>
                        <input
                            type="text"
                            value={form.symbol}
                            onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
                            placeholder="e.g. RELIANCE, TCS, INFY"
                            required
                            className="w-full px-4 py-2.5 bg-white/5 border border-[#2A2A2A] rounded-xl text-[#F0F0F0] placeholder:text-[#606060] focus:outline-none focus:border-[#1A6FD4]/50 focus:ring-1 focus:ring-[#3A6FF8]/20 transition-all"
                        />
                    </div>

                    {/* Buy Price + Quantity row */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-xs font-medium text-[#A0A0A0] mb-1.5 uppercase tracking-wider">
                                Buy Price (₹) *
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={form.buyPrice}
                                onChange={(e) => setForm({ ...form, buyPrice: e.target.value })}
                                placeholder="1250.00"
                                required
                                className="w-full px-4 py-2.5 bg-white/5 border border-[#2A2A2A] rounded-xl text-[#F0F0F0] placeholder:text-[#606060] focus:outline-none focus:border-[#1A6FD4]/50 focus:ring-1 focus:ring-[#3A6FF8]/20 transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-[#A0A0A0] mb-1.5 uppercase tracking-wider">
                                Quantity *
                            </label>
                            <input
                                type="number"
                                step="1"
                                min="1"
                                value={form.quantity}
                                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                                placeholder="10"
                                required
                                className="w-full px-4 py-2.5 bg-white/5 border border-[#2A2A2A] rounded-xl text-[#F0F0F0] placeholder:text-[#606060] focus:outline-none focus:border-[#1A6FD4]/50 focus:ring-1 focus:ring-[#3A6FF8]/20 transition-all"
                            />
                        </div>
                    </div>

                    {/* Buy Date */}
                    <div>
                        <label className="block text-xs font-medium text-[#A0A0A0] mb-1.5 uppercase tracking-wider">
                            Buy Date *
                        </label>
                        <input
                            type="date"
                            value={form.buyDate}
                            onChange={(e) => setForm({ ...form, buyDate: e.target.value })}
                            required
                            className="w-full px-4 py-2.5 bg-white/5 border border-[#2A2A2A] rounded-xl text-[#F0F0F0] focus:outline-none focus:border-[#1A6FD4]/50 focus:ring-1 focus:ring-[#3A6FF8]/20 transition-all"
                        />
                    </div>

                    {/* Notes */}
                    <div>
                        <label className="block text-xs font-medium text-[#A0A0A0] mb-1.5 uppercase tracking-wider">
                            Notes (optional)
                        </label>
                        <input
                            type="text"
                            value={form.notes}
                            onChange={(e) => setForm({ ...form, notes: e.target.value })}
                            placeholder="e.g. Long term hold, bought on dip"
                            className="w-full px-4 py-2.5 bg-white/5 border border-[#2A2A2A] rounded-xl text-[#F0F0F0] placeholder:text-[#606060] focus:outline-none focus:border-[#1A6FD4]/50 focus:ring-1 focus:ring-[#3A6FF8]/20 transition-all"
                        />
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        className="w-full py-3 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white font-semibold rounded-xl transition-all shadow-sm shadow-blue-500/20 hover:shadow-blue-500/30 mt-2"
                    >
                        {editingHolding ? "Update Holding" : "Add to Portfolio"}
                    </button>
                </form>
            </div>
        </div>
    );
}

// ── Main Portfolio Page ──────────────────────────────────────────────

export function PortfolioPage() {
    const [holdings, setHoldings] = useState<PortfolioHolding[]>([]);
    const [enriched, setEnriched] = useState<EnrichedHolding[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingHolding, setEditingHolding] = useState<PortfolioHolding | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [priceFetchStatus, setPriceFetchStatus] = useState<string>("");

    // Load holdings from localStorage
    const loadHoldings = useCallback(() => {
        const h = getHoldings();
        setHoldings(h);
    }, []);

    useEffect(() => {
        loadHoldings();
    }, [loadHoldings]);

    // Fetch current prices for all holdings
    const fetchCurrentPrices = useCallback(async () => {
        if (holdings.length === 0) {
            setEnriched([]);
            return;
        }

        setIsLoading(true);
        setPriceFetchStatus("Fetching live prices...");

        const results: EnrichedHolding[] = [];

        for (const h of holdings) {
            const totalInvested = h.buyPrice * h.quantity;
            try {
                const stockData = await fetchStockData(h.symbol);
                const currentPrice = stockData.currentPrice;
                const currentValue = currentPrice * h.quantity;
                const pnl = currentValue - totalInvested;
                const pnlPercent = totalInvested > 0 ? (pnl / totalInvested) * 100 : 0;

                results.push({
                    ...h,
                    currentPrice,
                    totalInvested,
                    currentValue,
                    pnl,
                    pnlPercent,
                });
            } catch {
                results.push({
                    ...h,
                    currentPrice: null,
                    totalInvested,
                    currentValue: null,
                    pnl: null,
                    pnlPercent: null,
                });
            }
        }

        setEnriched(results);
        setIsLoading(false);
        setPriceFetchStatus("");
    }, [holdings]);

    useEffect(() => {
        fetchCurrentPrices();
    }, [fetchCurrentPrices]);

    // CRUD handlers
    const handleSave = (data: HoldingFormData) => {
        if (editingHolding) {
            updateHolding(editingHolding.id, {
                symbol: data.symbol,
                buyPrice: parseFloat(data.buyPrice),
                quantity: parseInt(data.quantity),
                buyDate: data.buyDate,
                notes: data.notes,
            });
        } else {
            addHolding({
                symbol: data.symbol,
                buyPrice: parseFloat(data.buyPrice),
                quantity: parseInt(data.quantity),
                buyDate: data.buyDate,
                notes: data.notes,
            });
        }
        setEditingHolding(null);
        loadHoldings();
    };

    const handleEdit = (h: PortfolioHolding) => {
        setEditingHolding(h);
        setIsModalOpen(true);
    };

    const handleDelete = (id: string) => {
        deleteHolding(id);
        loadHoldings();
    };

    const handleAddNew = () => {
        setEditingHolding(null);
        setIsModalOpen(true);
    };

    // Portfolio summary
    const totalInvested = enriched.reduce((sum, h) => sum + h.totalInvested, 0);
    const totalCurrentValue = enriched.reduce(
        (sum, h) => sum + (h.currentValue ?? h.totalInvested),
        0
    );
    const totalPnl = totalCurrentValue - totalInvested;
    const totalPnlPercent = totalInvested > 0 ? (totalPnl / totalInvested) * 100 : 0;
    const isProfitable = totalPnl >= 0;

    return (
        <div className="min-h-screen text-[#F0F0F0] p-6 relative">
            {/* Background */}
            <div className="fixed inset-0 pointer-events-none z-[-1]">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-900/10 rounded-full blur-[120px]" />
            </div>

            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-2">
                    <div>
                        <h1 className="text-[2rem] font-bold text-[#F0F0F0] mb-1 tracking-tight flex items-center gap-3">
                            <div className="p-2.5 rounded-xl bg-[#1A6FD4]/10 border border-[#1A6FD4]/20">
                                <Briefcase className="size-6 text-[#4A9EFF]" />
                            </div>
                            My Portfolio
                        </h1>
                        <p className="text-[#A0A0A0] text-base ml-[52px]">
                            Track your holdings with live P&amp;L from NSE
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={fetchCurrentPrices}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-4 py-2.5 text-[#A0A0A0] hover:text-[#F0F0F0] hover:bg-white/5 rounded-xl transition-all border border-[#2A2A2A]"
                        >
                            <RefreshCw className={`size-4 ${isLoading ? "animate-spin" : ""}`} />
                            <span className="hidden sm:inline text-sm">Refresh</span>
                        </button>
                        <button
                            onClick={handleAddNew}
                            className="flex items-center gap-2 px-5 py-2.5 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white font-semibold rounded-xl transition-all shadow-sm shadow-blue-500/20 hover:shadow-blue-500/30"
                        >
                            <Plus size={18} />
                            <span className="hidden sm:inline">Add Stock</span>
                        </button>
                    </div>
                </div>

                {/* ── Portfolio Summary Cards ──────────────────────────── */}
                {holdings.length > 0 && (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Total Invested */}
                        <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A]">
                            <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                                <IndianRupee size={15} />
                                <span className="text-[10px] uppercase tracking-widest font-semibold">
                                    Total Invested
                                </span>
                            </div>
                            <p className="text-2xl font-bold text-[#F0F0F0]">
                                ₹{totalInvested.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                            </p>
                            <p className="text-xs text-[#A0A0A0] mt-1">
                                {holdings.length} stock{holdings.length !== 1 ? "s" : ""}
                            </p>
                        </div>

                        {/* Current Value */}
                        <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A]">
                            <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                                <BarChart3 size={15} />
                                <span className="text-[10px] uppercase tracking-widest font-semibold">
                                    Current Value
                                </span>
                            </div>
                            <p className="text-2xl font-bold text-[#F0F0F0]">
                                {isLoading ? (
                                    <Loader2 className="size-5 animate-spin text-[#A0A0A0]" />
                                ) : (
                                    `₹${totalCurrentValue.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`
                                )}
                            </p>
                            <p className="text-xs text-[#A0A0A0] mt-1">Live NSE prices</p>
                        </div>

                        {/* Total P&L */}
                        <div
                            className={`backdrop-blur-xl p-5 rounded-2xl border ${isProfitable
                                    ? "bg-emerald-500/5 border-[#4CAF7D]/20"
                                    : "bg-red-500/5 border-[#E05252]/20"
                                }`}
                        >
                            <div className="flex items-center gap-2 text-[#A0A0A0] mb-3">
                                {isProfitable ? <TrendingUp size={15} /> : <TrendingDown size={15} />}
                                <span className="text-[10px] uppercase tracking-widest font-semibold">
                                    Total P&amp;L
                                </span>
                            </div>
                            <p
                                className={`text-2xl font-bold ${isProfitable ? "text-[#4CAF7D]" : "text-[#E05252]"
                                    }`}
                            >
                                {isLoading ? (
                                    <Loader2 className="size-5 animate-spin text-[#A0A0A0]" />
                                ) : (
                                    <>
                                        {isProfitable ? "+" : ""}₹
                                        {Math.abs(totalPnl).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                                    </>
                                )}
                            </p>
                            <p
                                className={`text-xs mt-1 font-medium ${isProfitable ? "text-[#4CAF7D]" : "text-[#E05252]"
                                    }`}
                            >
                                {isProfitable ? "+" : ""}
                                {totalPnlPercent.toFixed(2)}%
                            </p>
                        </div>

                        {/* P&L Indicator */}
                        <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl p-5 rounded-2xl border border-[#2A2A2A] flex flex-col items-center justify-center">
                            <div
                                className={`p-3 rounded-full mb-2 ${isProfitable ? "bg-[#4CAF7D]/10" : "bg-[#E05252]/10"
                                    }`}
                            >
                                {isProfitable ? (
                                    <ArrowUpRight className="size-8 text-[#4CAF7D]" />
                                ) : (
                                    <ArrowDownRight className="size-8 text-[#E05252]" />
                                )}
                            </div>
                            <p
                                className={`text-sm font-semibold ${isProfitable ? "text-[#4CAF7D]" : "text-[#E05252]"
                                    }`}
                            >
                                {isProfitable ? "In Profit" : "In Loss"}
                            </p>
                        </div>
                    </div>
                )}

                {/* ── Holdings Table ──────────────────────────────────── */}
                {holdings.length === 0 ? (
                    <div className="h-[350px] flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#2A2A2A] bg-[#1E1E1E]/20">
                        <Briefcase className="size-12 text-[#606060] mb-4" />
                        <p className="text-[#A0A0A0] text-lg font-medium mb-1">
                            No holdings yet
                        </p>
                        <p className="text-[#A0A0A0] text-sm mb-5">
                            Add your first stock to start tracking your portfolio
                        </p>
                        <button
                            onClick={handleAddNew}
                            className="flex items-center gap-2 px-6 py-3 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white font-semibold rounded-xl transition-all shadow-sm shadow-blue-500/20"
                        >
                            <Plus size={18} />
                            Add Your First Stock
                        </button>
                    </div>
                ) : (
                    <div className="bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-xl rounded-2xl border border-[#2A2A2A] overflow-hidden">
                        {/* Loading bar */}
                        {isLoading && (
                            <div className="px-5 py-2 bg-[#1A6FD4]/5 border-b border-[#1A6FD4]/10 flex items-center gap-2">
                                <Loader2 className="size-3 text-[#4A9EFF] animate-spin" />
                                <span className="text-xs text-[#4A9EFF]">{priceFetchStatus}</span>
                            </div>
                        )}

                        {/* Table */}
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-[#2A2A2A]">
                                        <th className="text-left px-5 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Stock
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Qty
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Buy Price
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Current
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Invested
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            P&amp;L
                                        </th>
                                        <th className="text-right px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            P&amp;L %
                                        </th>
                                        <th className="text-center px-4 py-3.5 text-[10px] text-[#A0A0A0] font-semibold uppercase tracking-widest">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {enriched.map((h) => {
                                        const hasPnl = h.pnl !== null;
                                        const isProfit = (h.pnl ?? 0) >= 0;
                                        return (
                                            <tr
                                                key={h.id}
                                                className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
                                            >
                                                {/* Stock */}
                                                <td className="px-5 py-4">
                                                    <p className="text-sm font-semibold text-[#F0F0F0]">
                                                        {h.symbol}
                                                    </p>
                                                    <p className="text-[10px] text-[#A0A0A0] mt-0.5">
                                                        {h.buyDate}
                                                        {h.notes ? ` · ${h.notes}` : ""}
                                                    </p>
                                                </td>

                                                {/* Qty */}
                                                <td className="text-right px-4 py-4 text-sm text-[#F0F0F0] font-medium">
                                                    {h.quantity}
                                                </td>

                                                {/* Buy Price */}
                                                <td className="text-right px-4 py-4 text-sm text-[#A0A0A0]">
                                                    ₹{h.buyPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                                                </td>

                                                {/* Current Price */}
                                                <td className="text-right px-4 py-4 text-sm">
                                                    {h.currentPrice !== null ? (
                                                        <span className="text-[#F0F0F0] font-medium">
                                                            ₹{h.currentPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                                                        </span>
                                                    ) : (
                                                        <span className="text-[#606060]">—</span>
                                                    )}
                                                </td>

                                                {/* Invested */}
                                                <td className="text-right px-4 py-4 text-sm text-[#A0A0A0]">
                                                    ₹{h.totalInvested.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                                                </td>

                                                {/* P&L */}
                                                <td className="text-right px-4 py-4 text-sm font-semibold">
                                                    {hasPnl ? (
                                                        <span className={isProfit ? "text-[#4CAF7D]" : "text-[#E05252]"}>
                                                            {isProfit ? "+" : ""}₹
                                                            {Math.abs(h.pnl!).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                                                        </span>
                                                    ) : (
                                                        <span className="text-[#606060]">—</span>
                                                    )}
                                                </td>

                                                {/* P&L % */}
                                                <td className="text-right px-4 py-4">
                                                    {hasPnl ? (
                                                        <span
                                                            className={`inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-1 rounded-lg ${isProfit
                                                                    ? "bg-[#4CAF7D]/10 text-[#4CAF7D]"
                                                                    : "bg-[#E05252]/10 text-[#E05252]"
                                                                }`}
                                                        >
                                                            {isProfit ? (
                                                                <ArrowUpRight size={12} />
                                                            ) : (
                                                                <ArrowDownRight size={12} />
                                                            )}
                                                            {isProfit ? "+" : ""}
                                                            {h.pnlPercent!.toFixed(2)}%
                                                        </span>
                                                    ) : (
                                                        <span className="text-[#606060] text-xs">—</span>
                                                    )}
                                                </td>

                                                {/* Actions */}
                                                <td className="text-center px-4 py-4">
                                                    <div className="flex items-center justify-center gap-1">
                                                        <button
                                                            onClick={() => handleEdit(h)}
                                                            className="p-2 rounded-lg hover:bg-[#1A6FD4]/10 text-[#A0A0A0] hover:text-[#4A9EFF] transition-colors"
                                                            title="Edit"
                                                        >
                                                            <Pencil size={14} />
                                                        </button>
                                                        <button
                                                            onClick={() => handleDelete(h.id)}
                                                            className="p-2 rounded-lg hover:bg-[#E05252]/10 text-[#A0A0A0] hover:text-[#E05252] transition-colors"
                                                            title="Delete"
                                                        >
                                                            <Trash2 size={14} />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="mt-8 pt-6 border-t border-[rgba(74, 158, 255, 0.15)]">
                    <p className="text-center text-[10px] text-[#A0A0A0] uppercase tracking-widest">
                        QuantPulse India • Portfolio data stored locally in your browser • {new Date().getFullYear()}
                    </p>
                </div>
            </div>

            {/* Add / Edit Modal */}
            <HoldingModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setEditingHolding(null);
                }}
                onSave={handleSave}
                editingHolding={editingHolding}
            />
        </div>
    );
}
