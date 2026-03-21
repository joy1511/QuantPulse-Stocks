/**
 * Portfolio Store — localStorage CRUD for stock holdings
 *
 * Stores the user's manually-entered stock portfolio
 * (buy price, quantity, date, notes) in localStorage.
 *
 * Exposes getPortfolioContext() for feeding into AI agent analysis.
 */

// ── Types ────────────────────────────────────────────────────────────

export interface PortfolioHolding {
    id: string;
    symbol: string;       // e.g. "RELIANCE"
    buyPrice: number;     // price per share at purchase
    quantity: number;     // number of shares
    buyDate: string;      // ISO date string (YYYY-MM-DD)
    notes: string;        // optional user notes
    createdAt: string;    // ISO timestamp of when entry was added
}

/** Live-enriched holding (with current price + P&L) */
export interface EnrichedHolding extends PortfolioHolding {
    currentPrice: number | null;
    totalInvested: number;
    currentValue: number | null;
    pnl: number | null;
    pnlPercent: number | null;
}

// ── Constants ────────────────────────────────────────────────────────

const STORAGE_KEY = "quantpulse_portfolio";

// ── Helpers ──────────────────────────────────────────────────────────

function generateId(): string {
    return `h_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

// ── CRUD ─────────────────────────────────────────────────────────────

export function getHoldings(): PortfolioHolding[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return [];
        return JSON.parse(raw) as PortfolioHolding[];
    } catch {
        return [];
    }
}

export function addHolding(
    holding: Omit<PortfolioHolding, "id" | "createdAt">
): PortfolioHolding {
    const newHolding: PortfolioHolding = {
        ...holding,
        symbol: holding.symbol.toUpperCase().replace(/\.(NS|BO)$/i, ""),
        id: generateId(),
        createdAt: new Date().toISOString(),
    };

    const holdings = getHoldings();
    holdings.push(newHolding);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(holdings));
    return newHolding;
}

export function updateHolding(
    id: string,
    updates: Partial<Omit<PortfolioHolding, "id" | "createdAt">>
): PortfolioHolding | null {
    const holdings = getHoldings();
    const idx = holdings.findIndex((h) => h.id === id);
    if (idx === -1) return null;

    holdings[idx] = { ...holdings[idx], ...updates };
    if (updates.symbol) {
        holdings[idx].symbol = updates.symbol.toUpperCase().replace(/\.(NS|BO)$/i, "");
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(holdings));
    return holdings[idx];
}

export function deleteHolding(id: string): boolean {
    const holdings = getHoldings();
    const filtered = holdings.filter((h) => h.id !== id);
    if (filtered.length === holdings.length) return false;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    return true;
}

// ── Agent context helper ─────────────────────────────────────────────

/**
 * Returns a summary string of the user's portfolio,
 * suitable for injecting as extra context into the AI agent prompt.
 */
export function getPortfolioContext(): string {
    const holdings = getHoldings();
    if (holdings.length === 0) return "";

    const lines = holdings.map(
        (h) =>
            `- ${h.symbol}: ${h.quantity} shares @ ₹${h.buyPrice.toFixed(2)} (bought ${h.buyDate})`
    );

    return [
        "## User Portfolio (for context)",
        `The user holds ${holdings.length} stock(s):`,
        ...lines,
    ].join("\n");
}
