/**
 * Broker Integration Service
 * Handles broker connections, OAuth, and portfolio sync
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

export interface BrokerInfo {
  id: string;
  name: string;
  auth_type: 'credentials' | 'oauth' | 'token';
  fields_required: string[];
}

export interface BrokerConnection {
  broker: string;
  status: 'pending' | 'active' | 'error';
  connected_at: string;
  last_synced_at: string;
}

export interface Holding {
  symbol: string;
  exchange: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  pnl: number;
  pnl_percentage: number;
  source?: string;
}

export interface ConnectBrokerRequest {
  broker_id: string;
  credentials: Record<string, string>;
}

export interface ConnectBrokerResponse {
  status: string;
  broker: string;
  login_url?: string;
  message: string;
}

export interface SyncResponse {
  status: string;
  broker: string;
  holdings: Holding[];
  last_synced: string;
  total_holdings: number;
}

export interface BrokerStatusResponse {
  connected_brokers: BrokerConnection[];
  total_holdings: number;
}

class BrokerService {
  /**
   * Get list of supported brokers
   */
  async getSupportedBrokers(): Promise<BrokerInfo[]> {
    const data = await fetchAPI('/api/broker/supported');
    return data.brokers;
  }

  /**
   * Connect to a broker
   */
  async connectBroker(request: ConnectBrokerRequest): Promise<ConnectBrokerResponse> {
    return await fetchAPI('/api/broker/connect', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Sync portfolio from broker(s)
   */
  async syncBroker(brokerId?: string): Promise<SyncResponse> {
    return await fetchAPI('/api/broker/sync', {
      method: 'POST',
      body: JSON.stringify({ broker_id: brokerId || null }),
    });
  }

  /**
   * Get broker connection status
   */
  async getBrokerStatus(): Promise<BrokerStatusResponse> {
    return await fetchAPI('/api/broker/status');
  }

  /**
   * Disconnect from a broker
   */
  async disconnectBroker(brokerId: string): Promise<{ status: string; message: string; holdings_removed: number }> {
    return await fetchAPI(`/api/broker/disconnect?broker_id=${brokerId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Open OAuth window and handle callback
   */
  openOAuthWindow(loginUrl: string): Promise<{ success: boolean; error?: string }> {
    return new Promise((resolve) => {
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const popup = window.open(
        loginUrl,
        'Broker OAuth',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      if (!popup) {
        resolve({ success: false, error: 'Popup blocked. Please allow popups for this site.' });
        return;
      }

      // Poll for popup closure
      const pollTimer = setInterval(() => {
        if (popup.closed) {
          clearInterval(pollTimer);
          // Check if connection was successful by fetching status
          this.getBrokerStatus()
            .then(() => resolve({ success: true }))
            .catch((error) => resolve({ success: false, error: error.message }));
        }
      }, 500);
    });
  }
}

export const brokerService = new BrokerService();
export default brokerService;
