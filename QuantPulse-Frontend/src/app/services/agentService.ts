/**
 * Agent Service
 * Handles calling individual AI agent microservices with progress tracking
 */

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://quantpulse-stocks-backend.onrender.com");

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Types
export interface TechnicalData {
  ticker: string;
  lstm: {
    probability: number;
    outlook: string;
    confidence: string;
  };
  regime: {
    regime: string;
    confidence: number;
  };
  vix_level: number;
  features: {
    rsi: number;
    macd: number;
    bollinger_pctb: number;
  };
  stock_price: {
    current_price: number | null;
    previous_close: number | null;
  };
}

export interface FundamentalistResult {
  analysis: string;
  sentiment: string; // BULLISH, NEUTRAL, BEARISH
}

export interface TechnicianResult {
  analysis: string;
  confirmation: string; // CONFIRMS or CONTRADICTS
}

export interface RiskManagerResult {
  report: string;
  technical_summary: string;
}

export interface AgentAnalysisResult {
  ticker: string;
  technical: TechnicalData;
  fundamentalist: FundamentalistResult;
  technician: TechnicianResult;
  riskManager: RiskManagerResult;
}

class AgentService {
  /**
   * Get technical data (LSTM, regime, VIX, features)
   */
  async getTechnicalData(ticker: string): Promise<TechnicalData> {
    return await fetchAPI(`/api/v2/technical-data/${ticker}`);
  }

  /**
   * Call Fundamentalist agent
   */
  async callFundamentalist(ticker: string, vixLevel: number): Promise<FundamentalistResult> {
    return await fetchAPI('/api/agents/fundamentalist', {
      method: 'POST',
      body: JSON.stringify({
        ticker,
        vix_level: vixLevel
      })
    });
  }

  /**
   * Call Technician agent
   */
  async callTechnician(
    ticker: string,
    lstmProbability: number,
    lstmOutlook: string,
    rsi: number,
    macd: number,
    bollingerPctb: number
  ): Promise<TechnicianResult> {
    return await fetchAPI('/api/agents/technician', {
      method: 'POST',
      body: JSON.stringify({
        ticker,
        lstm_probability: lstmProbability,
        lstm_outlook: lstmOutlook,
        rsi,
        macd,
        bollinger_pctb: bollingerPctb
      })
    });
  }

  /**
   * Call Risk Manager agent
   */
  async callRiskManager(
    ticker: string,
    regime: string,
    regimeConfidence: number,
    vixLevel: number,
    lstmProbability: number,
    lstmOutlook: string,
    fundamentalistAnalysis: string,
    fundamentalistSentiment: string,
    technicianAnalysis: string,
    technicianConfirmation: string
  ): Promise<RiskManagerResult> {
    return await fetchAPI('/api/agents/risk-manager', {
      method: 'POST',
      body: JSON.stringify({
        ticker,
        regime,
        regime_confidence: regimeConfidence,
        vix_level: vixLevel,
        lstm_probability: lstmProbability,
        lstm_outlook: lstmOutlook,
        fundamentalist_analysis: fundamentalistAnalysis,
        fundamentalist_sentiment: fundamentalistSentiment,
        technician_analysis: technicianAnalysis,
        technician_confirmation: technicianConfirmation
      })
    });
  }

  /**
   * Run complete agent analysis with progress tracking
   */
  async analyzeWithAgents(
    ticker: string,
    onProgress?: (step: number, message: string) => void
  ): Promise<AgentAnalysisResult> {
    try {
      // Step 1: Get technical data
      onProgress?.(1, 'Getting technical data...');
      const technical = await this.getTechnicalData(ticker);

      // Step 2: Call Fundamentalist agent
      onProgress?.(2, 'Searching news (Fundamentalist)...');
      const fundamentalist = await this.callFundamentalist(ticker, technical.vix_level);

      // Step 3: Call Technician agent
      onProgress?.(3, 'Analyzing technicals (Technician)...');
      const technician = await this.callTechnician(
        ticker,
        technical.lstm.probability,
        technical.lstm.outlook,
        technical.features.rsi,
        technical.features.macd,
        technical.features.bollinger_pctb
      );

      // Step 4: Call Risk Manager agent
      onProgress?.(4, 'Generating final report (Risk Manager)...');
      const riskManager = await this.callRiskManager(
        ticker,
        technical.regime.regime,
        technical.regime.confidence,
        technical.vix_level,
        technical.lstm.probability,
        technical.lstm.outlook,
        fundamentalist.analysis,
        fundamentalist.sentiment,
        technician.analysis,
        technician.confirmation
      );

      onProgress?.(5, 'Complete!');

      return {
        ticker,
        technical,
        fundamentalist,
        technician,
        riskManager
      };
    } catch (error) {
      throw error;
    }
  }
}

export const agentService = new AgentService();
export default agentService;
