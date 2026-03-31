/**
 * Portfolio Store — MongoDB-backed CRUD for stock holdings
 *
 * Stores the user's manually-entered stock portfolio
 * (buy price, quantity, date, notes) in MongoDB via backend API.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────

export interface PortfolioHolding {
    id: string;
    symbol: string;       // e.g. "RELIANCE"
    buyPrice: number;     // price per share at purchase (camelCase for frontend)
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

// Backend API response format (snake_case)
interface HoldingAPIResponse {
    id: string;
    symbol: string;
    buy_price: number;
    quantity: number;
    buy_date: string;
    notes: string;
    created_at: string;
    user_id: string;
}

// ── Helpers ──────────────────────────────────────────────────────────

function getAuthToken(): string | null {
    return localStorage.getItem("auth_token");
}

function toFrontendFormat(apiHolding: HoldingAPIResponse): PortfolioHolding {
    return {
        id: apiHolding.id,
        symbol: apiHolding.symbol,
        buyPrice: apiHolding.buy_price,
        quantity: apiHolding.quantity,
        buyDate: apiHolding.buy_date,
        notes: apiHolding.notes,
        createdAt: apiHolding.created_at
    };
}

// ── CRUD ─────────────────────────────────────────────────────────────

export async function getHoldings(): Promise<PortfolioHolding[]> {
    const token = getAuthToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Failed to fetch holdings");
        }

        const apiHoldings: HoldingAPIResponse[] = await response.json();
        return apiHoldings.map(toFrontendFormat);
    } catch (error) {
        console.error("Error fetching holdings:", error);
        return [];
    }
}

export async function addHolding(
    holding: Omit<PortfolioHolding, "id" | "createdAt">
): Promise<PortfolioHolding> {
    const token = getAuthToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    // Convert to API format (snake_case)
    const apiData = {
        symbol: holding.symbol.toUpperCase().replace(/\.(NS|BO)$/i, ""),
        buy_price: holding.buyPrice,
        quantity: holding.quantity,
        buy_date: holding.buyDate,
        notes: holding.notes
    };

    const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(apiData)
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to add holding" }));
        throw new Error(error.detail || "Failed to add holding");
    }

    const apiHolding: HoldingAPIResponse = await response.json();
    return toFrontendFormat(apiHolding);
}

export async function updateHolding(
    id: string,
    updates: Partial<Omit<PortfolioHolding, "id" | "createdAt">>
): Promise<PortfolioHolding | null> {
    const token = getAuthToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    // Convert to API format (snake_case)
    const apiData: any = {};
    if (updates.symbol !== undefined) {
        apiData.symbol = updates.symbol.toUpperCase().replace(/\.(NS|BO)$/i, "");
    }
    if (updates.buyPrice !== undefined) {
        apiData.buy_price = updates.buyPrice;
    }
    if (updates.quantity !== undefined) {
        apiData.quantity = updates.quantity;
    }
    if (updates.buyDate !== undefined) {
        apiData.buy_date = updates.buyDate;
    }
    if (updates.notes !== undefined) {
        apiData.notes = updates.notes;
    }

    const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings/${id}`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(apiData)
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to update holding" }));
        throw new Error(error.detail || "Failed to update holding");
    }

    const apiHolding: HoldingAPIResponse = await response.json();
    return toFrontendFormat(apiHolding);
}

export async function deleteHolding(id: string): Promise<boolean> {
    const token = getAuthToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to delete holding" }));
        throw new Error(error.detail || "Failed to delete holding");
    }

    return true;
}

// ── Agent context helper ─────────────────────────────────────────────

/**
 * Returns a summary string of the user's portfolio,
 * suitable for injecting as extra context into the AI agent prompt.
 */
export async function getPortfolioContext(): Promise<string> {
    const holdings = await getHoldings();
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
