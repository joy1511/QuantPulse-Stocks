/**
 * Broker Selection Modal
 * Allows users to choose and connect their broker
 */

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, ExternalLink } from 'lucide-react';
import brokerService, { BrokerInfo } from '../services/brokerService';

interface BrokerSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const BROKER_INFO: Record<string, { name: string; logo: string }> = {
  angel_one: {
    name: 'Angel One',
    logo: '/assets/brokers/angel-one.png'
  },
  groww: {
    name: 'Groww',
    logo: '/assets/brokers/groww.png'
  },
  dhan: {
    name: 'Dhan',
    logo: '/assets/brokers/dhan.png'
  },
  paytm_money: {
    name: 'Paytm Money',
    logo: '/assets/brokers/paytm-money.png'
  }
};

const BROKER_SETUP_GUIDES: Record<string, string> = {
  angel_one: 'https://smartapi.angelone.in/docs',
  groww: 'https://groww.in/trade-api',
  dhan: 'https://dhanhq.co/docs/',
  paytm_money: 'https://www.paytmmoney.com/blog/open-api'
};

export default function BrokerSelectionModal({ isOpen, onClose, onSuccess }: BrokerSelectionModalProps) {
  const [step, setStep] = useState<'select' | 'credentials'>('select');
  const [selectedBroker, setSelectedBroker] = useState<BrokerInfo | null>(null);
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brokers] = useState<BrokerInfo[]>([
    { id: 'angel_one', name: 'Angel One', auth_type: 'credentials', fields_required: ['api_key', 'client_code', 'password', 'totp_token'] },
    { id: 'groww', name: 'Groww', auth_type: 'oauth', fields_required: ['api_key', 'api_secret'] },
    { id: 'dhan', name: 'Dhan', auth_type: 'token', fields_required: ['client_id', 'access_token'] },
    { id: 'paytm_money', name: 'Paytm Money', auth_type: 'oauth', fields_required: ['api_key', 'api_secret'] }
  ]);

  const handleBrokerSelect = (broker: BrokerInfo) => {
    setSelectedBroker(broker);
    setCredentials({});
    setError(null);
    setStep('credentials');
  };

  const handleCredentialChange = (field: string, value: string) => {
    setCredentials(prev => ({ ...prev, [field]: value }));
  };

  const handleConnect = async () => {
    if (!selectedBroker) return;

    setLoading(true);
    setError(null);

    try {
      const response = await brokerService.connectBroker({
        broker_id: selectedBroker.id,
        credentials
      });

      if (response.login_url) {
        // OAuth flow - open popup
        const result = await brokerService.openOAuthWindow(response.login_url);
        if (result.success) {
          onSuccess();
          handleClose();
        } else {
          setError(result.error || 'OAuth authentication failed');
        }
      } else {
        // Direct authentication successful
        onSuccess();
        handleClose();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to connect broker');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep('select');
    setSelectedBroker(null);
    setCredentials({});
    setError(null);
    onClose();
  };

  const getFieldLabel = (field: string): string => {
    const labels: Record<string, string> = {
      api_key: 'API Key',
      api_secret: 'API Secret',
      client_code: 'Client Code',
      client_id: 'Client ID',
      password: 'Password',
      totp_token: 'TOTP Token',
      access_token: 'Access Token'
    };
    return labels[field] || field;
  };

  const getFieldType = (field: string): string => {
    return field.includes('password') || field.includes('secret') || field.includes('token') ? 'password' : 'text';
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px] bg-[rgba(30,30,30,0.95)] border-[#2A2A2A]">
        <DialogHeader>
          <DialogTitle className="text-[#F0F0F0]">
            {step === 'select' ? 'Choose Your Broker' : `Connect to ${selectedBroker?.name}`}
          </DialogTitle>
        </DialogHeader>

        {step === 'select' && (
          <div className="space-y-4">
            <p className="text-sm text-[#A0A0A0]">
              Select your broker to automatically sync your portfolio
            </p>

            <div className="grid grid-cols-2 gap-3">
              {brokers.map((broker) => {
                const info = BROKER_INFO[broker.id];
                return (
                  <button
                    key={broker.id}
                    onClick={() => handleBrokerSelect(broker)}
                    className="group relative flex flex-col items-center gap-3 p-6 border border-[#2A2A2A] bg-[#1E1E1E] rounded-xl hover:border-[#1A6FD4] hover:bg-[#1A6FD4]/5 transition-all"
                  >
                    {/* Logo */}
                    <div className="w-20 h-20 rounded-2xl overflow-hidden bg-white shadow-lg group-hover:scale-105 transition-transform">
                      <img 
                        src={info.logo} 
                        alt={info.name}
                        className="w-full h-full object-contain"
                      />
                    </div>
                    
                    {/* Broker name */}
                    <span className="text-sm font-semibold text-[#F0F0F0] group-hover:text-white transition-colors">
                      {info.name}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {step === 'credentials' && selectedBroker && (
          <div className="space-y-4">
            <Alert className="bg-[#1A6FD4]/10 border-[#1A6FD4]/30">
              <AlertDescription className="flex items-center justify-between text-[#F0F0F0]">
                <span className="text-sm">Need help getting API credentials?</span>
                <a
                  href={BROKER_SETUP_GUIDES[selectedBroker.id]}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#4A9EFF] hover:text-[#6BB0FF] hover:underline flex items-center gap-1 text-sm"
                >
                  Setup Guide <ExternalLink className="h-3 w-3" />
                </a>
              </AlertDescription>
            </Alert>

            <div className="space-y-3">
              {selectedBroker.fields_required.map((field) => (
                <div key={field} className="space-y-1">
                  <Label htmlFor={field} className="text-[#F0F0F0]">{getFieldLabel(field)}</Label>
                  <Input
                    id={field}
                    type={getFieldType(field)}
                    value={credentials[field] || ''}
                    onChange={(e) => handleCredentialChange(field, e.target.value)}
                    placeholder={`Enter ${getFieldLabel(field)}`}
                    className="bg-[#1E1E1E] border-[#2A2A2A] text-[#F0F0F0] placeholder:text-[#606060]"
                  />
                </div>
              ))}
            </div>

            {error && (
              <Alert variant="destructive" className="bg-red-500/10 border-red-500/30">
                <AlertDescription className="text-red-400">{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep('select')}
                disabled={loading}
                className="flex-1 bg-[#1E1E1E] border-[#2A2A2A] text-[#F0F0F0] hover:bg-[#2A2A2A]"
              >
                Back
              </Button>
              <Button
                onClick={handleConnect}
                disabled={loading || !selectedBroker.fields_required.every(f => credentials[f])}
                className="flex-1 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Connect
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
