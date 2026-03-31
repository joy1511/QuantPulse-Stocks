# QuantPulse - Quick Start Guide

## 🚀 System Status: ✅ FULLY OPERATIONAL

Both frontend and backend are running successfully on your local machine.

## 📍 Access Points

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:5173 | ✅ Running |
| **Backend API** | http://localhost:8000 | ✅ Running |
| **API Docs** | http://localhost:8000/docs | ✅ Available |
| **Health Check** | http://localhost:8000/health | ✅ Healthy |

## 🔧 Running Services

### Backend (Terminal ID: 14)
- **Command**: `python run.py`
- **Directory**: `QuantPulse-Backend`
- **Port**: 8000
- **Database**: SQLite (local) + MongoDB Atlas (cloud)
- **Stock Provider**: IndianAPI (Premium tier)
- **Status**: Serving real-time NSE stock data

### Frontend (Terminal ID: 3)
- **Command**: `npm run dev`
- **Directory**: `QuantPulse-Frontend`
- **Port**: 5173
- **Framework**: React + Vite
- **Status**: Connected to local backend

## 🧪 Quick Tests

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Stock Quote
```bash
curl http://localhost:8000/stock/RELIANCE
```

### Test Frontend
Open browser: http://localhost:5173

## 📝 Environment Configuration

### Backend (.env)
```env
✅ GROQ_API_KEY - AI agent brain
✅ SERPER_API_KEY - News & search
✅ INDIANAPI_KEY - Stock data (Premium)
✅ MONGODB_URL - Database connection
✅ LOG_LEVEL - Set to INFO (reduces noise)
✅ PORT - 8000
```

### Frontend (.env)
```env
✅ VITE_API_BASE_URL - http://localhost:8000 (local dev)
✅ VITE_EMAILJS_* - Contact form credentials
```

## 🛠️ Common Commands

### Start Backend
```bash
cd QuantPulse-Backend
python run.py
```

### Start Frontend
```bash
cd QuantPulse-Frontend
npm run dev
```

### Stop Services
Press `Ctrl+C` in the respective terminal

### View Backend Logs
Check Terminal ID: 14

### View Frontend Logs
Check Terminal ID: 3

## 🔍 API Endpoints

### Stock Data
- `GET /stock/{symbol}` - Get stock quote
- `GET /stock/{symbol}/historical?period=1mo` - Historical data
- `GET /stock/{symbol}/profile` - Company profile
- `POST /stock/quotes` - Multiple quotes

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Portfolio
- `GET /portfolio` - Get user portfolio
- `POST /portfolio/add` - Add stock to portfolio
- `DELETE /portfolio/{symbol}` - Remove from portfolio

### Analysis (V2)
- `POST /api/v2/analyze` - AI-powered stock analysis

### Market Data
- `GET /market/movers` - Top gainers/losers
- `GET /market/indices` - Market indices

## 📊 Current Test Results

### RELIANCE Stock Quote
```json
{
  "symbol": "RELIANCE",
  "currentPrice": 1343.90,
  "change": -4.20,
  "changePercent": -0.31%,
  "volume": 24.39M,
  "isDemoData": false,
  "provider": "IndianAPI"
}
```

## 🐛 Troubleshooting

### Backend won't start
1. Check if port 8000 is available
2. Verify .env file exists with all keys
3. Check MongoDB connection string
4. Review logs in terminal

### Frontend won't connect
1. Verify backend is running on port 8000
2. Check VITE_API_BASE_URL in frontend .env
3. Clear browser cache
4. Check browser console for errors

### MongoDB connection issues
1. Verify MONGODB_URL in .env
2. Check internet connection
3. Verify MongoDB Atlas cluster is running
4. Check IP whitelist in MongoDB Atlas

### Stock data not loading
1. Check INDIANAPI_KEY is set
2. Verify API key is valid
3. Check backend logs for errors
4. Test endpoint directly: `curl http://localhost:8000/stock/RELIANCE`

## 📚 Documentation

- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend ReDoc**: http://localhost:8000/redoc (Alternative docs)
- **MongoDB Setup**: `QuantPulse-Backend/MONGODB_SETUP_GUIDE.md`
- **Startup Fix**: `QuantPulse-Backend/STARTUP_FIX_SUMMARY.md`

## 🎯 Next Steps

1. **Test the application**: Open http://localhost:5173 in your browser
2. **Create an account**: Sign up and verify email
3. **Search for stocks**: Try RELIANCE, TCS, INFY, HDFCBANK
4. **Add to portfolio**: Build your watchlist
5. **Get AI analysis**: Use the War Room feature

## 🔐 Security Notes

- Never commit .env files to git
- Keep API keys secure
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Set proper CORS origins for production

## 🚀 Deployment

### For Production (Vercel/Render)
- Frontend .env should use production backend URL
- Backend .env should use production MongoDB
- Set all environment variables in hosting platform
- Enable HTTPS
- Configure proper CORS origins

---

**Status**: ✅ All systems operational
**Last Updated**: March 31, 2026
**Version**: 2.0.0
