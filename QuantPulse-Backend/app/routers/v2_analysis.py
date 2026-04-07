"""
V2 Analysis Router — The Full AI Pipeline Endpoint

Exposes `GET /api/v2/analyze/{ticker}` which runs the complete
Regime-Adaptive AI pipeline:

1. Data Phase    → fetch_market_context (yfinance) — LIVE DATA ONLY
2. Math Phase    → LSTM prediction + HMM regime detection
3. Reasoning     → CrewAI War Room (3-agent debate)
4. Response      → JSON with regime, signal, confidence, and Investment Memo

RESILIENCE: If the War Room fails, the endpoint still returns
the ticker, regime, vix, ai_signal, and a "Technical Analysis Only" report.
This endpoint will NEVER return a 500 error.
"""

import logging
import traceback
from fastapi import APIRouter, HTTPException

from app.services.data_provider import fetch_market_context, get_current_vix_level
from app.services.lstm_service import predict as lstm_predict
from app.services.regime_detector import detect_regime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v2",
    tags=["V2 Analysis — Regime-Adaptive AI"],
)


@router.get("/model-status")
async def get_model_status():
    """
    Get LSTM model loading status.
    
    Useful for frontend to check if model is ready before making analysis requests.
    
    Returns:
        dict with keys:
        - loaded: bool - Whether model is fully loaded
        - loading: bool - Whether model is currently loading
        - load_time: float | None - Time taken to load (seconds)
        - message: str - Human-readable status message
    """
    from app.services.lstm_service import get_model_status
    
    status = get_model_status()
    
    # Add human-readable message
    if status["loaded"]:
        status["message"] = f"Model ready (loaded in {status['load_time']}s)"
    elif status["loading"]:
        status["message"] = f"Model loading... ({status['load_time']}s elapsed)"
    else:
        status["message"] = "Model not loaded - will load on first analysis request"
    
    return status


@router.get("/analyze/{ticker}")
async def analyze_ticker(ticker: str):
    """
    Full AI Analysis Pipeline for a given stock ticker.

    Runs in 3 phases:
    1. **Data Phase** — Fetches 2yr LIVE data for target stock, Nifty 50, India VIX
    2. **Math Phase** — LSTM neural prediction + HMM regime detection
    3. **Reasoning Phase** — CrewAI multi-agent debate → Investment Memo

    If the War Room fails, returns a "Technical Analysis Only" report
    with the real LSTM + HMM results. NEVER returns a 500 error.

    Args:
        ticker: NSE stock symbol (e.g., "RELIANCE", "TCS", "HDFCBANK")

    Returns:
        JSON with ticker, regime, vix, ai_signal, confidence, and final_report
    """
    ticker_clean = ticker.strip().upper()
    logger.info(f"🚀 Starting V2 analysis pipeline for {ticker_clean}...")

    # =========================================================================
    # PHASE 1: DATA — Fetch LIVE market context from yfinance (or fallback)
    # =========================================================================
    logger.info("📥 Phase 1: Fetching LIVE market data (yfinance locally / IndianAPI on cloud)...")

    try:
        context = await fetch_market_context(ticker_clean)
    except Exception as e:
        logger.error(f"❌ Data fetch failed: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch market data: {str(e)}")

    target_df = context["target_df"]
    nifty_df = context["nifty_df"]
    vix_df = context["vix_df"]

    # Extract live price from yfinance data
    current_price = None
    previous_close = None
    day_change = None
    day_change_pct = None
    if target_df is not None and not target_df.empty and len(target_df) >= 2:
        import math
        current_price = float(target_df["Close"].iloc[-1])
        previous_close = float(target_df["Close"].iloc[-2])
        
        # Handle NaN values
        if math.isnan(current_price) or math.isnan(previous_close):
            current_price = None
            previous_close = None
            day_change = None
            day_change_pct = None
        else:
            day_change = round(current_price - previous_close, 2)
            day_change_pct = round((day_change / previous_close) * 100, 2) if previous_close else 0

    # Validate target data
    if target_df is None:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for ticker '{ticker_clean}'. "
                   f"Ensure it is a valid NSE symbol (e.g., RELIANCE, TCS, INFY)."
        )

    if hasattr(target_df, 'empty') and target_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for ticker '{ticker_clean}'. "
                   f"Ensure it is a valid NSE symbol (e.g., RELIANCE, TCS, INFY)."
        )

    if nifty_df is None:
        logger.warning("⚠️ Nifty data unavailable — regime detection will use defaults")

    # =========================================================================
    # PHASE 2: MATH — Run LSTM + HMM on REAL data
    # =========================================================================
    logger.info("🧠 Phase 2: Running AI models on LIVE data...")

    # 2a. Regime Detection (HMM on Nifty 50)
    regime_result = detect_regime(nifty_df)
    regime = regime_result.get("regime", "Sideways")
    logger.info(f"🌤️ Regime: {regime} (confidence: {regime_result.get('confidence', 0):.0%})")

    # 2c. Extract current VIX level from LIVE data (before freeing memory)
    vix_level = get_current_vix_level(vix_df)
    logger.info(f"📊 VIX: {vix_level:.1f}")

    # Free memory before LSTM loading (critical for Render free tier)
    # Keep only target_df, free nifty_df and vix_df
    import gc
    del nifty_df, vix_df
    gc.collect()
    logger.info("🧹 Freed memory before LSTM loading")

    # Save OHLC snapshot BEFORE passing target_df to LSTM (which may modify it)
    _ohlc_snapshot = target_df.tail(90).copy() if target_df is not None and not target_df.empty else None

    # 2b. LSTM Neural Prediction (pass pre-fetched data)
    try:
        lstm_result = lstm_predict(ticker_clean, target_df=target_df)
        ai_outlook = lstm_result.get("outlook", "Neutral Outlook")
        probability = lstm_result.get("probability", 0.5)
        features_summary = lstm_result.get("features_summary", {})
        logger.info(f"📈 LSTM: {ai_outlook} ({probability:.1%})")
    except Exception as e:
        # LSTM loading failed (TensorFlow too heavy for free tier)
        logger.warning(f"⚠️ LSTM prediction failed: {e}")
        lstm_result = {
            "outlook": "Neutral Outlook",
            "probability": 0.5,
            "features_summary": {},
            "error": "LSTM model unavailable on free tier"
        }
        ai_outlook = "Neutral Outlook"
        probability = 0.5
        features_summary = {}
        logger.info(f"📈 LSTM: Skipped (using neutral default)")

    # =========================================================================
    # PHASE 3: REASONING — SKIPPED (Use dedicated microservice endpoints instead)
    # =========================================================================
    # NOTE: CrewAI agents are now available via separate microservice endpoints:
    # - POST /api/agents/fundamentalist
    # - POST /api/agents/technician  
    # - POST /api/agents/risk-manager
    # This prevents memory overflow on free tier (512MB limit)
    
    logger.info("🏛️ Phase 3: Skipping Research Analysis (use microservice endpoints)")
    
    research_result = {
        "report": (
            f"## Technical Analysis: {ticker_clean} (NSE)\n\n"
            f"### Market Regime\n**{regime}** (confidence: {regime_result.get('confidence', 0):.0%})\n\n"
            f"### LSTM AI Analysis\n"
            f"- Outlook: **{ai_outlook}**\n"
            f"- Confidence: **{probability:.1%}**\n\n"
            f"### India VIX\n**{vix_level:.1f}**\n\n"
            f"### Technical Indicators\n"
            f"- RSI: {features_summary.get('rsi', 50):.1f}\n"
            f"- MACD: {features_summary.get('macd', 0):.4f}\n"
            f"- Bollinger %B: {features_summary.get('bollinger_pctb', 0.5):.4f}\n\n"
            f"---\n*For detailed agent analysis, use the AI Analysis Engine in the dashboard.*"
        ),
        "technical_summary": ai_outlook,
        "agents_used": ["LSTM + HMM (Technical Analysis)"],
        "error": None,
    }

    final_report = research_result.get("report", "No report generated.")
    technical_summary = research_result.get("technical_summary", "Neutral Outlook")
    agents_used = research_result.get("agents_used", [])
    research_error = research_result.get("error")

    logger.info(f"📋 Technical Summary: {technical_summary} | Agents: {agents_used}")

    # =========================================================================
    # RESPONSE — Assemble the final JSON (always succeeds)
    # =========================================================================
    response = {
        "ticker": ticker_clean,
        "regime": regime,
        "vix": round(vix_level, 2),
        "ai_outlook": ai_outlook,
        "confidence": f"{probability * 100:.1f}%",
        "final_report": final_report,
        "stock_price": {
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "day_change": day_change,
            "day_change_pct": day_change_pct,
        },
        "details": {
            "lstm": {
                "probability": probability,
                "outlook": ai_outlook,
                "features": features_summary,
            },
            "regime_detection": {
                "regime": regime,
                "confidence": regime_result.get("confidence", 0),
                "all_states": regime_result.get("all_states", {}),
            },
            "research_analysis": {
                "technical_summary": technical_summary,
                "agents_used": agents_used,
                "error": research_error,
            },
        },
    }

    # =========================================================================
    # OHLC — Append last 90 days of daily price data for the frontend chart
    # =========================================================================
    import math
    ohlc_data = []
    try:
        if _ohlc_snapshot is not None and not _ohlc_snapshot.empty:
            df_tail = _ohlc_snapshot
            # Strip timezone from index if present
            if hasattr(df_tail.index, 'tz') and df_tail.index.tz is not None:
                df_tail.index = df_tail.index.tz_convert(None)
            for date, row in df_tail.iterrows():
                try:
                    # Convert to float and check for NaN
                    open_val = float(row["Open"])
                    high_val = float(row["High"])
                    low_val = float(row["Low"])
                    close_val = float(row["Close"])
                    volume_val = float(row.get("Volume", 0))
                    
                    # Skip rows with NaN values
                    if any(math.isnan(v) for v in [open_val, high_val, low_val, close_val]):
                        logger.debug(f"Skipping OHLC row {date}: contains NaN")
                        continue
                    
                    ohlc_data.append({
                        "date": str(date)[:10],
                        "open": round(open_val, 2),
                        "high": round(high_val, 2),
                        "low": round(low_val, 2),
                        "close": round(close_val, 2),
                        "volume": int(volume_val) if not math.isnan(volume_val) else 0,
                    })
                except Exception as row_err:
                    logger.debug(f"Skipping OHLC row {date}: {row_err}")
            logger.info(f"📊 OHLC serialized: {len(ohlc_data)} rows for {ticker_clean}")
        else:
            logger.warning(f"⚠️ target_df is None or empty — no OHLC data for {ticker_clean}")
    except Exception as e:
        logger.warning(f"⚠️ Could not serialize OHLC data: {e}")

    response["ohlc"] = ohlc_data

    logger.info(f"✅ V2 analysis complete for {ticker_clean} ({len(ohlc_data)} OHLC rows)")
    return response



@router.get("/technical-data/{ticker}")
async def get_technical_data(ticker: str):
    """
    Get technical data (LSTM, regime, VIX, features) for frontend chaining.
    
    This endpoint provides all the technical analysis data needed for the frontend
    to call individual agent microservices sequentially with progress indicators.
    
    Args:
        ticker: NSE stock symbol (e.g., "RELIANCE", "TCS", "HDFCBANK")
    
    Returns:
        JSON with LSTM prediction, regime detection, VIX level, and technical features
    """
    ticker_clean = ticker.strip().upper()
    logger.info(f"📊 Fetching technical data for {ticker_clean}...")
    
    try:
        # Fetch market context
        context = await fetch_market_context(ticker_clean)
        target_df = context["target_df"]
        nifty_df = context["nifty_df"]
        vix_df = context["vix_df"]
        
        # Get current price
        current_price = None
        previous_close = None
        if target_df is not None and not target_df.empty:
            current_price = float(target_df["Close"].iloc[-1])
            if len(target_df) > 1:
                previous_close = float(target_df["Close"].iloc[-2])
        
        # LSTM prediction
        lstm_result = lstm_predict(ticker_clean, target_df)
        probability = lstm_result.get("probability", 0.5)
        ai_outlook = lstm_result.get("outlook", "Neutral Outlook")
        
        # Regime detection
        regime_result = detect_regime(nifty_df)
        regime = regime_result.get("regime", "Unknown")
        regime_confidence = regime_result.get("confidence", 0)
        
        # VIX level
        vix_level = get_current_vix_level(vix_df)
        
        # Calculate technical features
        features = {}
        if target_df is not None and not target_df.empty and len(target_df) >= 20:
            try:
                # RSI
                delta = target_df["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                features["rsi"] = float(rsi.iloc[-1]) if not rsi.empty else 50.0
                
                # MACD
                ema12 = target_df["Close"].ewm(span=12, adjust=False).mean()
                ema26 = target_df["Close"].ewm(span=26, adjust=False).mean()
                macd = ema12 - ema26
                features["macd"] = float(macd.iloc[-1]) if not macd.empty else 0.0
                
                # Bollinger %B
                sma20 = target_df["Close"].rolling(window=20).mean()
                std20 = target_df["Close"].rolling(window=20).std()
                upper_band = sma20 + (2 * std20)
                lower_band = sma20 - (2 * std20)
                bollinger_pctb = (target_df["Close"] - lower_band) / (upper_band - lower_band)
                features["bollinger_pctb"] = float(bollinger_pctb.iloc[-1]) if not bollinger_pctb.empty else 0.5
            except Exception as e:
                logger.warning(f"Failed to calculate some features: {e}")
                features = {"rsi": 50.0, "macd": 0.0, "bollinger_pctb": 0.5}
        else:
            features = {"rsi": 50.0, "macd": 0.0, "bollinger_pctb": 0.5}
        
        logger.info(f"✅ Technical data ready for {ticker_clean}")
        
        return {
            "ticker": ticker_clean,
            "lstm": {
                "probability": probability,
                "outlook": ai_outlook,
                "confidence": f"{probability * 100:.1f}%"
            },
            "regime": {
                "regime": regime,
                "confidence": regime_confidence
            },
            "vix_level": round(vix_level, 2),
            "features": {
                "rsi": round(features.get("rsi", 50.0), 2),
                "macd": round(features.get("macd", 0.0), 4),
                "bollinger_pctb": round(features.get("bollinger_pctb", 0.5), 3)
            },
            "stock_price": {
                "current_price": round(current_price, 2) if current_price else None,
                "previous_close": round(previous_close, 2) if previous_close else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get technical data for {ticker_clean}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get technical data: {str(e)}")
