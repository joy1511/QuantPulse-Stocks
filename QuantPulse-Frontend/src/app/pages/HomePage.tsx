import { Link } from 'react-router-dom';
import { BarChart3, TrendingUp, Brain, Shield, Zap, Target } from 'lucide-react';
import { Card } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { useAuth } from '@/app/context/AuthContext';

export function HomePage() {
  const { user } = useAuth();
  const features = [
    {
      icon: Brain,
      title: 'AI-Driven Predictions',
      description: 'Advanced machine learning algorithms analyze market patterns and technical indicators.'
    },
    {
      icon: TrendingUp,
      title: 'Real-Time Analytics',
      description: 'Get instant insights on NSE stocks with live price updates and sentiment analysis.'
    },
    {
      icon: Shield,
      title: 'Research-Focused',
      description: 'Built for analysis, not speculation. All outputs are research signals, not financial advice.'
    },
    {
      icon: Zap,
      title: 'Fast Analysis',
      description: 'LSTM inference and regime detection run in seconds on live NSE data.'
    },
    {
      icon: Target,
      title: 'Technical Depth',
      description: 'RSI, MACD, Bollinger Bands - all computed fresh from real price history.'
    },
    {
      icon: BarChart3,
      title: 'Advanced Charts',
      description: 'Interactive visualizations with technical indicators and pattern recognition.'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-6 overflow-hidden">
        <div className="max-w-6xl mx-auto text-center relative">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[rgba(74,158,255,0.1)] border border-[rgba(74, 158, 255, 0.12)] mb-8 hover:bg-[rgba(74,158,255,0.15)] transition-colors cursor-default">
            <span className="size-2 rounded-full bg-[#1A6FD4] animate-pulse"></span>
            <span className="text-sm font-medium text-[#4A9EFF]">AI-Powered Stock Market Intelligence</span>
          </div>

          <h1 className="text-5xl md:text-[5rem] leading-[1.1] mb-6 font-bold tracking-tight text-[#F0F0F0]">
            QuantPulse India
          </h1>

          <p className="text-xl md:text-2xl text-[#A0A0A0] mb-4 font-normal tracking-wide">
            Next-Generation Stock Market Research Deck
          </p>

          <p className="text-lg text-[#A0A0A0] mb-12 max-w-3xl mx-auto">
            Harness the power of data, statistical models, deep learning models, and artificial intelligence to study market movements on NSE stocks.
            Get real-time analysis and actionable insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-5 mt-10">
            {user ? (
              <Link to="/portfolio">
                <Button variant="prominent" size="lg" className="h-14 px-10 text-lg">
                  <BarChart3 className="size-5" />
                  Open Portfolio
                </Button>
              </Link>
            ) : (
              <Link to="/signin">
                <Button variant="prominent" size="lg" className="h-14 px-10 text-lg">
                  <Zap className="size-5" />
                  Sign In / Sign Up
                </Button>
              </Link>
            )}
            <Link to="/dashboard">
              <Button variant="secondary" size="lg" className="h-14 px-8 text-lg bg-[rgba(30, 30, 30, 0.9)]">
                <TrendingUp className="size-5" />
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl mb-4 text-[#F0F0F0] font-bold tracking-tight">
              Powered by Advanced Technology
            </h2>
            <p className="text-lg text-[#A0A0A0] max-w-2xl mx-auto leading-relaxed">
              Our platform combines cutting-edge AI with comprehensive market data to deliver
              actionable insights for Indian stock markets. Explore AI-powered research analytics for NSE stocks - LSTM predictions,
              HMM results, regime detection, multi-agent analysis and result verification with technical metrics  in one place.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={index}
                  className="p-8 h-full bg-[rgba(30, 30, 30, 0.9)] hover:bg-[rgba(30, 30, 30, 0.9)] border border-[#2A2A2A] hover:border-[#1A6FD4]/30 transition-all duration-300 group hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-500/10"
                >
                  <div className="p-3 rounded-xl bg-blue-500/10 group-hover:bg-blue-500/20 w-fit mb-6 transition-colors">
                    <Icon className="size-6 text-[#4A9EFF] group-hover:text-[#4A9EFF] transition-colors" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3 text-[#F0F0F0] transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-[#A0A0A0] leading-relaxed text-[0.95rem] transition-colors">
                    {feature.description}
                  </p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[rgba(74, 158, 255, 0.15)]">
        <div className="max-w-6xl mx-auto text-center text-[#A0A0A0] text-sm">
          <p>&copy; 2026 QuantPulse India. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
