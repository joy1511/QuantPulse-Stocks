# QuantPulse India - Architecture Overview

## System Architecture

QuantPulse India follows a modern full-stack architecture with clear separation between frontend, backend, and AI services.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + Vite + Tailwind CSS                   │
│  - Dashboard UI                                              │
│  - Real-time Charts                                          │
│  - Stock Search & Analysis                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTP/JSON)
┌────────────────────▼────────────────────────────────────────┐
│                         Backend                              │
│  FastAPI + Python 3.11                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (Routers)                                  │  │
│  │  - /api/v1/* - Stock data, market movers             │  │
│  │  - /api/v2/* - AI predictions, analysis              │  │
│  │  - /auth/* - User authentication                      │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Services Layer                                       │  │
│  │  - Agent Orchestrator (Multi-Agent AI)               │  │
│  │  - LSTM Service (Price Predictions)                  │  │
│  │  - Regime Detector (Market Classification)           │  │
│  │  - Stock Service (Data Aggregation)                  │  │
│  │  - Cache Service (Performance)                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Data Providers                                       │  │
│  │  - Finnhub (US & Global Markets)                     │  │
│  │  - TwelveData (Technical Data)                       │  │
│  │  - IndianAPI (NSE Real-time)                         │  │
│  │  - Serper (News Search)                              │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Data Storage                              │
│  - SQLite (User accounts, sessions)                         │
│  - MongoDB (Market data, predictions, cache)                │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Agent AI System

The "War Room" architecture uses three specialized AI agents powered by Groq + Llama 3.3 (70B):

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│     Agent Orchestrator (CrewAI)         │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  1. Fundamentalist Agent          │ │
│  │     - Searches financial news     │ │
│  │     - Analyzes macro conditions   │ │
│  │     - Evaluates market sentiment  │ │
│  │     Tool: SerperDevTool           │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│  ┌──────────▼────────────────────────┐ │
│  │  2. Technician Agent              │ │
│  │     - Reviews LSTM predictions    │ │
│  │     - Analyzes technical patterns │ │
│  │     - Evaluates indicators        │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│  ┌──────────▼────────────────────────┐ │
│  │  3. Risk Manager (Boss)           │ │
│  │     - Synthesizes all inputs      │ │
│  │     - Applies risk rules          │ │
│  │     - Makes final decision        │ │
│  │     - Generates report            │ │
│  └──────────┬────────────────────────┘ │
└─────────────┼───────────────────────────┘
              │
              ▼
        Final Report (JSON)
```

### Zero-Fail Design

The system has multiple fallback layers:
1. **Agent Success**: Normal multi-agent execution
2. **Timeout Fallback**: If agents take too long (>60s), return partial results
3. **Error Fallback**: If agents fail, return error report with available data
4. **Simulation Mode**: If all else fails, return simulated analysis

## LSTM Prediction Pipeline

```
Historical Data (60 days)
     │
     ▼
┌─────────────────────────────────────┐
│  Feature Engineering                │
│  - Log Returns                      │
│  - RSI (14-day)                     │
│  - MACD                             │
│  - Volatility (20-day)              │
│  - Bollinger %B                     │
│  - Normalized ATR                   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  LSTM Model (Bidirectional)         │
│  - Input: (60, 6) sequence          │
│  - Hidden layers with dropout       │
│  - Batch normalization              │
│  - Output: Probability (0-1)        │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Classification                      │
│  - Bullish: > 0.55                  │
│  - Neutral: 0.45 - 0.55             │
│  - Bearish: < 0.45                  │
└─────────────────────────────────────┘
```

## Market Regime Detection

```
Nifty 50 Data (30-90 days)
     │
     ▼
┌─────────────────────────────────────┐
│  Calculate Metrics                   │
│  - 30-day return                    │
│  - Annualized volatility            │
│  - Mean daily return                │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Rule-Based Classification           │
│                                     │
│  Bear/Volatile:                     │
│  - Return < -8% OR                  │
│  - (Return < -3% AND Vol > 25%)     │
│                                     │
│  Bull/Stable:                       │
│  - Return > +8% OR                  │
│  - (Return > +3% AND Vol < 20%)     │
│                                     │
│  Sideways:                          │
│  - Return between -3% and +3%       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Confidence Scoring (50-95%)        │
│  Based on signal strength           │
└─────────────────────────────────────┘
```

## Data Flow

### Stock Analysis Request

1. **User Input**: User enters stock symbol (e.g., "TCS")
2. **API Request**: Frontend calls `/api/v2/analyze/{symbol}`
3. **Data Aggregation**:
   - Fetch current price from providers
   - Retrieve historical data (60 days)
   - Get market regime (Nifty 50)
4. **LSTM Prediction**:
   - Load model (cached after first use)
   - Engineer features from historical data
   - Generate prediction probability
5. **AI Agent Analysis**:
   - Fundamentalist searches news
   - Technician analyzes LSTM + indicators
   - Risk Manager synthesizes and decides
6. **Response**: Return comprehensive analysis to frontend
7. **Caching**: Store results in MongoDB for 5 minutes

### Performance Optimizations

- **Model Caching**: LSTM model loaded once, kept in memory
- **Data Caching**: Market data cached for 5 minutes
- **Lazy Loading**: Model loads on first prediction request
- **Provider Fallback**: Multiple data sources with automatic failover
- **Request Timeouts**: Frontend enforces timeouts to prevent hanging

## Security

- **Environment Variables**: Sensitive keys stored in `.env` (not committed)
- **CORS**: Configured to allow only frontend domain
- **Input Validation**: Pydantic schemas validate all API inputs
- **Rate Limiting**: Planned for production deployment
- **Authentication**: JWT-based auth for user endpoints

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────┐
│  Vercel (Frontend)                                       │
│  - Static React build                                   │
│  - CDN distribution                                     │
│  - Automatic HTTPS                                      │
└────────────────┬────────────────────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────────────────────┐
│  Render (Backend)                                        │
│  - Python 3.11.9 runtime                                │
│  - Uvicorn ASGI server                                  │
│  - Environment variables                                │
│  - Health checks                                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  MongoDB Atlas (Database)                                │
│  - M0 Free Tier                                         │
│  - Automatic backups                                    │
│  - Global distribution                                  │
└─────────────────────────────────────────────────────────┘
```

## Technology Choices

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type safety with Pydantic
- Easy integration with ML models

### Why React + TypeScript?
- Component reusability
- Type safety reduces bugs
- Large ecosystem
- Excellent developer experience

### Why MongoDB?
- Flexible schema for market data
- Fast reads for cached data
- Easy scaling
- Free tier for development

### Why CrewAI?
- Simplified multi-agent orchestration
- Built-in task management
- Easy integration with LLMs
- Sequential and parallel execution

## Future Enhancements

- **Real-time Updates**: WebSocket for live price updates
- **Backtesting**: Historical strategy testing
- **Portfolio Tracking**: User portfolio management
- **Advanced Indicators**: More technical analysis tools
- **Mobile App**: React Native mobile application
- **Automated Tests**: Unit and integration test suite
- **CI/CD Pipeline**: Automated deployment
- **Monitoring**: Application performance monitoring
