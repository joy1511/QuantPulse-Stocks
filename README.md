# QuantPulse India

> AI-powered stock analytics platform for Indian NSE markets with multi-agent predictions and real-time sentiment analysis.

## Overview

QuantPulse India is a full-stack financial analytics platform that combines machine learning, multi-agent AI systems, and real-time market data to provide comprehensive stock analysis for the Indian National Stock Exchange (NSE).

### Key Features

- **Multi-Agent AI System**: Three specialized AI agents (Fundamentalist, Technician, Risk Manager) collaborate to generate investment insights
- **LSTM Price Predictions**: Deep learning model trained on historical NSE data for short-term momentum forecasting
- **Market Regime Detection**: Rule-based system to identify Bull/Stable, Bear/Volatile, or Sideways market conditions
- **Real-time Market Data**: Integration with multiple data providers (Finnhub, TwelveData, IndianAPI)
- **News Sentiment Analysis**: Automated sentiment scoring from financial news sources
- **Interactive Dashboard**: Real-time charts, market movers, and technical indicators

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Recharts for data visualization
- React Router for navigation

### Backend
- FastAPI (Python 3.11+)
- SQLite + MongoDB for data persistence
- TensorFlow/Keras for LSTM models
- CrewAI for multi-agent orchestration
- Groq API with Llama 3.3 (70B)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- MongoDB Atlas account (free tier)
- API keys for data providers

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/quantpulse.git
   cd quantpulse
   ```

2. **Setup Backend**
   ```bash
   cd QuantPulse-Backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys and MongoDB URL
   python run.py
   ```
   Backend runs at: http://localhost:8000

3. **Setup Frontend**
   ```bash
   cd QuantPulse-Frontend
   npm install
   cp .env.example .env
   # Edit .env with backend URL
   npm run dev
   ```
   Frontend runs at: http://localhost:5173

### Configuration

See [docs/MONGODB_SETUP.md](docs/MONGODB_SETUP.md) for MongoDB configuration.

Required environment variables:
- `MONGODB_URL`: MongoDB connection string
- `GROQ_API_KEY`: Groq API key for AI agents
- `SERPER_API_KEY`: Serper API key for news search
- `FINNHUB_API_KEY`: Finnhub API key for market data
- `TWELVEDATA_API_KEY`: TwelveData API key
- `INDIANAPI_KEY`: IndianAPI key for NSE data

## Project Structure

```
quantpulse/
├── QuantPulse-Backend/          # FastAPI backend
│   ├── app/
│   │   ├── models/              # Database models
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── agent_orchestrator.py    # Multi-agent AI system
│   │   │   ├── lstm_service.py          # LSTM predictions
│   │   │   └── regime_detector.py       # Market regime detection
│   │   └── providers/           # Data provider integrations
│   ├── models/                  # Trained ML models
│   └── requirements.txt
├── QuantPulse-Frontend/         # React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/      # React components
│   │   │   ├── pages/           # Page components
│   │   │   └── services/        # API client
│   │   └── main.tsx
│   └── package.json
└── docs/                        # Documentation
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Backend (Render)
- Configured via `render.yaml`
- Uses Python 3.11.9 runtime
- Set environment variables in Render dashboard

### Frontend (Vercel)
- Automatic deployment from Git
- Update `VITE_API_BASE_URL` to production backend URL
- Configure environment variables in Vercel dashboard

## Architecture

### Multi-Agent AI System
Three specialized agents collaborate using CrewAI:
1. **Fundamentalist**: Analyzes news, macro conditions, and market sentiment
2. **Technician**: Evaluates LSTM predictions and technical indicators
3. **Risk Manager**: Synthesizes inputs and makes final recommendations

### LSTM Model
- Bidirectional LSTM architecture
- Trained on 50-200 NSE stocks with 5-10 years of historical data
- Input: 60-day sequences with 6 technical features
- Output: Bullish/Neutral/Bearish probability

### Market Regime Detection
Rule-based system analyzing Nifty 50:
- 30-day returns and volatility
- Classifies into Bull/Stable, Bear/Volatile, or Sideways
- Confidence scoring based on signal strength

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for educational and informational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review API documentation at `/docs` endpoint

---

Built with ❤️ for the Indian stock market community
