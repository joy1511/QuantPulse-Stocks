# QuantPulse Backend

FastAPI backend service for QuantPulse India stock analytics platform.

## Features

- RESTful API for stock data and analysis
- Multi-agent AI system for investment insights
- LSTM-based price predictions
- Market regime detection
- Real-time data from multiple providers
- MongoDB and SQLite integration
- Automatic API documentation

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas account
- API keys (Groq, Serper, Finnhub, TwelveData, IndianAPI)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB URL

# Run server
python run.py
```

Server runs at: http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── models/              # Database models
├── routers/             # API endpoints
│   ├── auth.py         # Authentication
│   ├── market.py       # Market data
│   ├── v2_analysis.py  # AI analysis
│   └── health.py       # Health checks
├── services/            # Business logic
│   ├── agent_orchestrator.py    # Multi-agent AI
│   ├── lstm_service.py          # LSTM predictions
│   ├── regime_detector.py       # Market regime
│   └── stock_service.py         # Stock data
├── providers/           # Data provider integrations
├── schemas/             # Pydantic schemas
├── config.py           # Configuration
├── database.py         # SQLite setup
├── mongodb.py          # MongoDB setup
└── main.py             # FastAPI app
```

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/stock/{symbol}` | Stock quote |
| GET | `/api/v1/market-movers` | Top gainers/losers |
| POST | `/api/v2/analyze/{symbol}` | AI-powered analysis |
| GET | `/api/v2/model-status` | LSTM model status |
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | User login |

## Configuration

Required environment variables in `.env`:

```env
# Database
MONGODB_URL=mongodb+srv://...
DATABASE_URL=sqlite:///./quantpulse.db

# AI Services
GROQ_API_KEY=your_groq_key
SERPER_API_KEY=your_serper_key

# Data Providers
FINNHUB_API_KEY=your_finnhub_key
TWELVEDATA_API_KEY=your_twelvedata_key
INDIANAPI_KEY=your_indianapi_key

# Application
SECRET_KEY=your_secret_key
LOG_LEVEL=INFO
```

See [../docs/MONGODB_SETUP.md](../docs/MONGODB_SETUP.md) for MongoDB setup.

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Check logs
tail -f logs/app.log
```

## Deployment

Configured for Render deployment via `render.yaml`:

- Python 3.11.9 runtime
- Automatic health checks
- Environment variables via dashboard
- Uvicorn ASGI server

## Architecture

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for detailed architecture documentation.

## License

MIT License - see [../LICENSE](../LICENSE) for details.
