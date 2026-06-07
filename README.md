# QuantPulse Stocks - AI-Powered Stock Analysis Platform

**Regime-Adaptive AI Analysis for Indian Stock Market (NSE/BSE)**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.17-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com/)

---

## 🎯 Overview

QuantPulse is an advanced stock analysis platform that combines **machine learning**, **multi-agent AI systems**, and **technical analysis** to provide comprehensive investment research for Indian equity markets.

### Key Features

- 🧠 **LSTM Neural Network** - Deep learning model for price prediction
- 🎭 **Hidden Markov Models** - Market regime detection (Bull/Bear/Sideways)
- 🤖 **AI Research Agents** - Multi-agent CrewAI system with 3 specialized analysts
- 📊 **Technical Indicators** - RSI, MACD, Bollinger Bands, ATR, and more
- 📰 **News Sentiment** - Real-time news analysis with sentiment scoring
- 🔄 **Multi-Provider Data** - yfinance, IndianAPI, nsepython with intelligent fallback
- 🚀 **Production-Ready** - Optimized for Render free tier deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Dashboard • Charts • Analysis • Portfolio                   │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  V2 Analysis Pipeline                                 │  │
│  │  ├─ Data Phase    → yfinance/IndianAPI               │  │
│  │  ├─ Math Phase    → LSTM + HMM                       │  │
│  │  └─ Reasoning     → CrewAI War Room (3 agents)       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                             │  │
│  │  • Agent Orchestrator  • LSTM Service                │  │
│  │  • Regime Detector     • Stock Service               │  │
│  │  • Cache Service       • Data Provider               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              External Services                               │
│  • Groq (LLM)  • Serper (Search)  • NewsAPI                 │
│  • Hugging Face (Model Storage)  • IndianAPI                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or poetry
- Git
- API keys (see Configuration section)

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/QuantPulse-Stocks.git
   cd QuantPulse-Stocks/QuantPulse-Backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

---

## 🌐 Deployment (Render Free Tier)

### Optimized for 512MB RAM

This project is **fully optimized** for Render free tier deployment:

✅ Memory-bounded caching (TTLCache)  
✅ Lazy model loading (LSTM loads on first request)  
✅ CPU-only TensorFlow (tensorflow-cpu)  
✅ Efficient connection pooling  
✅ Aggressive garbage collection  
✅ Graceful degradation (works without AI agents)  

### Deploy to Render

See **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** for complete step-by-step guide.

**Quick Steps**:
1. Fork/clone this repository
2. Create Render account
3. New Web Service → Connect GitHub
4. Configure environment variables
5. Deploy!

**Deployment Time**: ~8-10 minutes  
**Cold Start**: ~30-60 seconds (first request only)  
**Warm Requests**: ~200-500ms  

---

## ⚙️ Configuration

### Required Environment Variables

```bash
# Security (REQUIRED)
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# System
ENVIRONMENT=production
RENDER=true
```

### Recommended (Core Features)

```bash
# AI Features
GROQ_API_KEY=<your-groq-api-key>
SERPER_API_KEY=<your-serper-api-key>

# Stock Data
INDIANAPI_KEY=<optional-free-tier-works-without-key>

# News Sentiment
NEWSAPI_KEY=<your-newsapi-key>
```

### API Key Resources

| Service | Purpose | Free Tier | Link |
|---------|---------|-----------|------|
| **Groq** | LLM for AI agents | 10 req/sec | https://console.groq.com |
| **Serper** | Web search | 2,500/month | https://serper.dev |
| **IndianAPI** | NSE/BSE data | Unlimited | https://indianapi.in |
| **NewsAPI** | News sentiment | 100/day | https://newsapi.org |
| **Hugging Face** | Model storage | Unlimited | https://huggingface.co |

---

## 📊 API Endpoints

### Core Endpoints

#### Health Checks
```bash
GET /health                  # Basic health check
GET /health/detailed         # Detailed status + memory
GET /health/ready            # Kubernetes readiness
GET /health/live             # Kubernetes liveness
```

#### V2 Analysis (Primary)
```bash
GET /api/v2/analyze/{ticker}     # Full AI analysis
GET /api/v2/model-status         # LSTM model status
```

#### Stock Data
```bash
GET /stock/{symbol}              # Current quote + profile
GET /stock/{symbol}/historical   # Historical OHLCV
GET /api/market/trending         # Top gainers/losers
```

#### AI Predictions
```bash
POST /ai-prediction/{symbol}     # Technical + news analysis
POST /ensemble/predict           # Multi-agent prediction
```

### Example Request

```bash
# Full analysis for RELIANCE
curl https://your-api.onrender.com/api/v2/analyze/RELIANCE

# Response includes:
# - LSTM prediction (bullish/bearish/neutral)
# - Market regime (HMM: bull/bear/sideways)
# - Technical indicators (RSI, MACD, etc.)
# - AI agent research report (if GROQ_API_KEY set)
# - Risk assessment (VIX-adjusted)
```

---

## 🧠 AI Analysis System

### Three-Phase Pipeline

#### 1️⃣ **Data Phase**
- Fetches 2 years of OHLCV data
- Downloads Nifty 50 (market benchmark)
- Gets India VIX (volatility index)
- Sources: yfinance, IndianAPI, nsepython

#### 2️⃣ **Math Phase**
- **LSTM Neural Network**: Analyzes 60-day window with 6 features
  - Log returns, RSI, MACD, Volatility, Bollinger %B, ATR
  - Outputs probability (0-1) and outlook (Bullish/Neutral/Bearish)
  
- **Hidden Markov Model**: Detects market regime on Nifty 50
  - 3 states: Bull, Bear, Sideways
  - Uses returns volatility and trend direction

#### 3️⃣ **Reasoning Phase (AI Agents)**
- **Fundamentalist**: Researches news, macro conditions
- **Technician**: Validates LSTM with technical indicators
- **Risk Manager**: Synthesizes all data + risk assessment

### Fallback Strategy

If AI agents fail (no API key, timeout, error):
- ✅ Returns rule-based analysis using LSTM + HMM
- ✅ Provides technical summary
- ✅ **Never returns 500 error**

---

## 📈 Performance & Optimization

### Memory Budget (Render Free Tier)

| Component | Memory | Status |
|-----------|--------|--------|
| FastAPI Base | ~80 MB | ✅ Minimal |
| TensorFlow + LSTM | ~250 MB | ✅ CPU-only |
| CrewAI Agents | ~150 MB | ✅ Lazy load |
| Cache | ~50 MB | ✅ Bounded |
| Overhead | ~50 MB | System |
| **TOTAL** | **~480 MB** | ✅ Under 512MB |

### Optimizations Applied

1. **Bounded Cache** - TTLCache with 1000 entry limit
2. **Lazy Loading** - Models load on first request only
3. **Connection Pooling** - Limits concurrent connections
4. **Garbage Collection** - Aggressive cleanup after model load
5. **CPU-Only TensorFlow** - No GPU dependencies
6. **Request Limits** - Gunicorn restarts after 1000 requests

### Benchmarks

- **Cold Start**: 30-60s (model download + load)
- **Warm Requests**: 200-500ms (cached data)
- **LSTM Prediction**: 1-2s
- **Full AI Analysis**: 15-30s (CrewAI)
- **Memory Usage**: 400-480 MB steady state

---

## 🔒 Security

### Best Practices

✅ Strong SECRET_KEY (32+ bytes random)  
✅ API keys in environment (never in code)  
✅ Rate limiting (slowapi)  
✅ CORS restrictions (no wildcard)  
✅ SQL injection protection (parameterized queries)  
✅ Input validation (Pydantic models)  

### Security Checklist

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) → Security section

---

## 🐛 Troubleshooting

### Common Issues

#### Out of Memory (OOM)
**Symptoms**: Exit code 137, crashes  
**Solutions**: 
- Check `/health/detailed` for memory usage
- Disable AI agents: `FORCE_SIMULATION_MODE=true`
- Upgrade to Render Starter ($7/mo, 1GB RAM)

#### LSTM Returns Neutral Always
**Symptoms**: All predictions neutral  
**Solutions**:
- Check logs for TensorFlow errors
- Verify Hugging Face model download
- Ensure sufficient data (need 86+ days)

#### AI Agents Not Working
**Symptoms**: Fallback report always  
**Solutions**:
- Verify `GROQ_API_KEY` is set
- Check Groq API quota
- Test API key with curl

See **[docs/DEPLOYMENT_OPTIMIZATION.md](./docs/DEPLOYMENT_OPTIMIZATION.md)** for detailed troubleshooting.

---

## 📚 Documentation

- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment guide
- **[DEPLOYMENT_OPTIMIZATION.md](./docs/DEPLOYMENT_OPTIMIZATION.md)** - Technical optimization details
- **[FIXES_APPLIED.md](./FIXES_APPLIED.md)** - Complete list of fixes and improvements
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System architecture overview
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (Swagger)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **TensorFlow** - Deep learning (LSTM)
- **CrewAI** - Multi-agent AI orchestration
- **Groq** - Fast LLM inference
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation

### Data Sources
- **yfinance** - Historical stock data
- **nsepython** - NSE real-time data (no API key)
- **IndianAPI** - NSE/BSE FREE API
- **NewsAPI** - Financial news
- **Serper** - Web search

### Deployment
- **Render** - Cloud hosting (free tier optimized)
- **Gunicorn** - WSGI server
- **PostgreSQL** - Production database
- **Docker** - Containerization (optional)

---

## 📊 Supported Exchanges

- ✅ **NSE (National Stock Exchange)**
- ✅ **BSE (Bombay Stock Exchange)**
- ✅ **Indian Indices** (Nifty 50, Bank Nifty, Sensex)
- ✅ **India VIX** (Volatility Index)

**Stock Universe**: 2000+ NSE/BSE listed stocks

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/

# Lint
flake8 app/
```

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **Hugging Face** - Model hosting
- **IndianAPI** - FREE NSE/BSE data
- **Render** - Free tier hosting
- **CrewAI** - Multi-agent framework
- **TensorFlow** - Deep learning library

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@quantpulse.com (if applicable)

---

## 🚨 Disclaimer

**Important**: This software is for **educational and research purposes only**.

- ❌ **Not financial advice**
- ❌ **Not investment recommendations**  
- ❌ **Not guaranteed to be accurate**

Stock markets are inherently unpredictable. Past performance does not indicate future results. Always consult a qualified financial advisor before making investment decisions.

**Use at your own risk.**

---

## 🎯 Roadmap

### v2.1 (Next Release)
- [ ] Real-time WebSocket updates
- [ ] Portfolio backtesting
- [ ] Options analysis
- [ ] Multi-asset support (commodities, forex)

### v3.0 (Future)
- [ ] Mobile app (React Native)
- [ ] Advanced charting (TradingView integration)
- [ ] Social features (share analysis)
- [ ] Premium tier (paid features)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Built with ❤️ for Indian equity markets**

**Version**: 2.0.0 (Render-Optimized)  
**Last Updated**: June 7, 2026  
**Status**: ✅ Production Ready (Render Free Tier)

