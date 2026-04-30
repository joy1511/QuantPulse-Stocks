/**
 * Agent Analysis Component
 * Shows progressive AI analysis with real-time updates from each agent
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Loader2, CheckCircle2, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import agentService, { type AgentAnalysisResult } from '../services/agentService';
import ReactMarkdown from 'react-markdown';

interface AgentAnalysisProps {
  ticker: string;
  onComplete?: (result: AgentAnalysisResult) => void;
}

export default function AgentAnalysis({ ticker, onComplete }: AgentAnalysisProps) {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AgentAnalysisResult | null>(null);
  const [progressMessage, setProgressMessage] = useState('');

  const steps = [
    { id: 1, name: 'Technical Data', icon: '📊', description: 'LSTM, Regime, VIX' },
    { id: 2, name: 'Fundamentalist', icon: '📰', description: 'News Analysis' },
    { id: 3, name: 'Technician', icon: '📈', description: 'Technical Analysis' },
    { id: 4, name: 'Risk Manager', icon: '🎯', description: 'Final Report' }
  ];

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    setStep(0);
    setResult(null);

    try {
      const analysisResult = await agentService.analyzeWithAgents(
        ticker,
        (currentStep, message) => {
          setStep(currentStep);
          setProgressMessage(message);
        }
      );

      setResult(analysisResult);
      onComplete?.(analysisResult);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'BULLISH') return 'text-green-500 bg-green-500/10';
    if (sentiment === 'BEARISH') return 'text-red-500 bg-red-500/10';
    return 'text-gray-500 bg-gray-500/10';
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'BULLISH') return <TrendingUp className="h-4 w-4" />;
    if (sentiment === 'BEARISH') return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Run Analysis Button */}
      {!loading && !result && (
        <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
          <CardContent className="pt-6">
            <Button
              onClick={runAnalysis}
              disabled={loading}
              className="w-full bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white py-6 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Run AI Analysis'
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Progress Steps */}
      {loading && (
        <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
          <CardHeader>
            <CardTitle className="text-[#F0F0F0]">AI Analysis in Progress</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {steps.map((s) => (
              <div
                key={s.id}
                className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                  step === s.id
                    ? 'bg-[#1A6FD4]/10 border border-[#1A6FD4]/30'
                    : step > s.id
                    ? 'bg-green-500/10 border border-green-500/30'
                    : 'bg-[#1E1E1E] border border-[#2A2A2A]'
                }`}
              >
                <div className="text-2xl">{s.icon}</div>
                <div className="flex-1">
                  <div className="font-medium text-[#F0F0F0]">{s.name}</div>
                  <div className="text-xs text-[#A0A0A0]">{s.description}</div>
                </div>
                {step === s.id && (
                  <Loader2 className="h-5 w-5 animate-spin text-[#4A9EFF]" />
                )}
                {step > s.id && (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                )}
              </div>
            ))}
            {progressMessage && (
              <p className="text-sm text-[#4A9EFF] text-center mt-4">
                {progressMessage}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Alert variant="destructive" className="bg-red-500/10 border-red-500/30">
          <AlertDescription className="text-red-400">{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Technical Data */}
          <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
            <CardHeader>
              <CardTitle className="text-[#F0F0F0] flex items-center gap-2">
                📊 Technical Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-[#A0A0A0]">LSTM Prediction</p>
                  <p className="text-sm font-medium text-[#F0F0F0]">{result.technical.lstm.outlook}</p>
                  <p className="text-xs text-[#4A9EFF]">{result.technical.lstm.confidence}</p>
                </div>
                <div>
                  <p className="text-xs text-[#A0A0A0]">Market Regime</p>
                  <p className="text-sm font-medium text-[#F0F0F0]">{result.technical.regime.regime}</p>
                  <p className="text-xs text-[#4A9EFF]">{(result.technical.regime.confidence * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-xs text-[#A0A0A0]">VIX Level</p>
                  <p className="text-sm font-medium text-[#F0F0F0]">{result.technical.vix_level}</p>
                </div>
                <div>
                  <p className="text-xs text-[#A0A0A0]">RSI</p>
                  <p className="text-sm font-medium text-[#F0F0F0]">{result.technical.features.rsi}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Fundamentalist Analysis */}
          <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-[#F0F0F0] flex items-center gap-2">
                  📰 News Analysis
                </CardTitle>
                <Badge className={`${getSentimentColor(result.fundamentalist.sentiment)} flex items-center gap-1`}>
                  {getSentimentIcon(result.fundamentalist.sentiment)}
                  {result.fundamentalist.sentiment}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-[#E0E0E0] whitespace-pre-wrap">{result.fundamentalist.analysis}</p>
            </CardContent>
          </Card>

          {/* Technician Analysis */}
          <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-[#F0F0F0] flex items-center gap-2">
                  📈 Technical Analysis
                </CardTitle>
                <Badge className={result.technician.confirmation === 'CONFIRMS' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}>
                  {result.technician.confirmation} LSTM
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-[#E0E0E0] whitespace-pre-wrap">{result.technician.analysis}</p>
            </CardContent>
          </Card>

          {/* Final Report */}
          <Card className="bg-[rgba(30,30,30,0.9)] border-[#2A2A2A]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-[#F0F0F0] flex items-center gap-2">
                  🎯 Final Research Report
                </CardTitle>
                <Badge className="bg-[#1A6FD4]/20 text-[#4A9EFF]">
                  {result.riskManager.technical_summary}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown>{result.riskManager.report}</ReactMarkdown>
              </div>
            </CardContent>
          </Card>

          {/* Run Again Button */}
          <Button
            onClick={runAnalysis}
            variant="outline"
            className="w-full bg-[#1E1E1E] border-[#2A2A2A] text-[#F0F0F0] hover:bg-[#2A2A2A]"
          >
            🔄 Run Analysis Again
          </Button>
        </div>
      )}
    </div>
  );
}
