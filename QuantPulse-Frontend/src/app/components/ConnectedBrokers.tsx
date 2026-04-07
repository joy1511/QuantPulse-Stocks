/**
 * Connected Brokers Component
 * Displays connected brokers and allows sync/disconnect
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, RefreshCw, Unplug, CheckCircle2, Clock } from 'lucide-react';
import brokerService, { BrokerConnection } from '../services/brokerService';

interface ConnectedBrokersProps {
  onSync?: () => void;
}

const BROKER_NAMES: Record<string, string> = {
  angel_one: 'Angel One',
  groww: 'Groww',
  dhan: 'Dhan',
  paytm_money: 'Paytm Money'
};

const BROKER_LOGOS: Record<string, string> = {
  angel_one: '/assets/brokers/angel-one.png',
  groww: '/assets/brokers/groww.png',
  dhan: '/assets/brokers/dhan.png',
  paytm_money: '/assets/brokers/paytm-money.png'
};

export default function ConnectedBrokers({ onSync }: ConnectedBrokersProps) {
  const [connections, setConnections] = useState<BrokerConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = await brokerService.getBrokerStatus();
      setConnections(status.connected_brokers);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load broker connections');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async (brokerId: string) => {
    try {
      setSyncing(brokerId);
      setError(null);
      await brokerService.syncBroker(brokerId);
      await loadConnections();
      onSync?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync portfolio');
    } finally {
      setSyncing(null);
    }
  };

  const handleDisconnect = async (brokerId: string) => {
    if (!confirm(`Are you sure you want to disconnect from ${BROKER_NAMES[brokerId]}? This will remove all synced holdings.`)) {
      return;
    }

    try {
      setDisconnecting(brokerId);
      setError(null);
      await brokerService.disconnectBroker(brokerId);
      await loadConnections();
      onSync?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect broker');
    } finally {
      setDisconnecting(null);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (connections.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Connected Brokers</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {connections.map((connection) => {
          return (
            <div
              key={connection.broker}
              className="flex items-center justify-between p-3 border border-[#2A2A2A] rounded-lg bg-[#1E1E1E]"
            >
              <div className="flex items-center gap-3">
                {/* Logo */}
                <div className="w-12 h-12 rounded-lg overflow-hidden bg-white shadow-md flex-shrink-0">
                  <img 
                    src={BROKER_LOGOS[connection.broker]} 
                    alt={BROKER_NAMES[connection.broker]}
                    className="w-full h-full object-contain"
                  />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[#F0F0F0]">{BROKER_NAMES[connection.broker]}</span>
                    <Badge
                      variant={connection.status === 'active' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {connection.status === 'active' && <CheckCircle2 className="h-3 w-3 mr-1" />}
                      {connection.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                      {connection.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-[#A0A0A0]">
                    Last synced {formatDate(connection.last_synced_at)}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleSync(connection.broker)}
                  disabled={syncing === connection.broker || disconnecting === connection.broker}
                  className="bg-[#1E1E1E] border-[#2A2A2A] hover:bg-[#2A2A2A]"
                >
                  {syncing === connection.broker ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleDisconnect(connection.broker)}
                  disabled={syncing === connection.broker || disconnecting === connection.broker}
                  className="hover:bg-red-500/10 hover:text-red-400"
                >
                  {disconnecting === connection.broker ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Unplug className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
