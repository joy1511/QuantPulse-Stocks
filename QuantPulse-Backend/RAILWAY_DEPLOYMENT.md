# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

This backend is optimized for Railway deployment with zero build failures.

### Prerequisites
- Railway account (https://railway.app)
- API keys for stock data providers

### 1. Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

Or manually:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from this directory
cd QuantPulse-Backend
railway up
```

### 2. Configure Environment Variables

In your Railway dashboard, set these environment variables:

**Required for Live Data:**
```
TWELVEDATA_API_KEY=your_twelvedata_api_key
FINNHUB_API_KEY=your_finnhub_api_key
NEWSAPI_KEY=your_newsapi_key
```

**Optional Configuration:**
```
STOCK_PROVIDER=auto
LOG_LEVEL=INFO
CACHE_MAX_SIZE=10000
CACHE_DEFAULT_TTL=3600
```

**Note:** Railway automatically sets `PORT` and `RAILWAY_ENVIRONMENT`

### 3. Verify Deployment

After deployment, check:
- ✅ Service is running: `https://your-app.railway.app/`
- ✅ Health check: `https://your-app.railway.app/health`
- ✅ API docs: `https://your-app.railway.app/docs`
- ✅ Stock API: `https://your-app.railway.app/stock/RELIANCE`

### 4. Monitor Logs

```bash
railway logs
```

Look for these startup messages:
```
✅ TWELVEDATA_API_KEY loaded - primary provider available
✅ FINNHUB_API_KEY loaded - fallback provider available
📊 Running in LIVE MODE - serving real market data
🎯 Application startup complete - ready to serve requests
```

## 🔧 Deployment Features

### Production Optimizations
- ✅ Python 3.11.9 runtime (stable)
- ✅ Lightweight dependencies (no ML/CV libraries)
- ✅ 60-second caching for fast responses
- ✅ Request coalescing prevents API quota destruction
- ✅ Automatic provider fallback (TwelveData → Finnhub → Demo)
- ✅ Demo mode when no API keys configured

### Railway-Specific Features
- ✅ Automatic environment detection
- ✅ Dynamic PORT binding
- ✅ Procfile for reliable startup
- ✅ Runtime specification
- ✅ Zero-config deployment

### Error Handling
- ✅ Never crashes due to missing API keys
- ✅ Graceful degradation to demo data
- ✅ Comprehensive logging for debugging
- ✅ Health check endpoint for monitoring

## 🚨 Troubleshooting

### Build Failures
If build fails, check:
1. Python version is 3.11.9 (see `runtime.txt`)
2. No heavy ML dependencies in `requirements.txt`
3. All imports are available

### Runtime Issues
If app doesn't start:
1. Check Railway logs: `railway logs`
2. Verify environment variables are set
3. Test health endpoint: `/health`

### API Issues
If stock data doesn't work:
1. Check API key configuration in Railway dashboard
2. Verify logs show "LIVE MODE" not "DEMO MODE"
3. Test individual providers via service status: `/stock/service/status`

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Welcome message and service status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Stock Data
- `GET /stock/{symbol}` - Real-time stock quote
- `GET /stock/{symbol}/historical?period=1mo` - Historical data
- `GET /stock/{symbol}/profile` - Company profile
- `POST /stock/quotes?symbols=RELIANCE&symbols=TCS` - Multiple quotes

### Service Management
- `GET /stock/service/status` - Service health and provider status
- `DELETE /stock/{symbol}/cache` - Invalidate cache for symbol

## 🔐 Security Notes

- Never commit API keys to git
- Use Railway dashboard for environment variables
- Monitor API usage to avoid rate limits
- Enable CORS for your frontend domain

## 📈 Performance

- **Cold start**: ~2-3 seconds
- **Cached responses**: ~50ms
- **API calls**: ~500ms (with fallback)
- **Memory usage**: ~150MB
- **Build time**: ~2-3 minutes

## 🎯 Production Ready

This backend is production-ready with:
- ✅ Multi-provider redundancy
- ✅ Intelligent caching
- ✅ Error handling
- ✅ Monitoring endpoints
- ✅ Scalable architecture
- ✅ Zero-downtime deployments