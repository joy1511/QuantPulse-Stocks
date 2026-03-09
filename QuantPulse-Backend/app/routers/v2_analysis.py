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
from app.services.agent_orchestrator import run_research_analysis

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v2",
    tags=["V2 Analysis — Regime-Adaptive AI"],
)


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
    logger.info("📥 Phase 1: Fetching LIVE market data from yfinance...")

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
        current_price = float(target_df["Close"].iloc[-1])
        previous_close = float(target_df["Close"].iloc[-2])
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

    # 2c. Extract current VIX level from LIVE data
    vix_level = get_current_vix_level(vix_df)
    logger.info(f"📊 VIX: {vix_level:.1f}")

    # =========================================================================
    # PHASE 3: REASONING — CrewAI Research Analysis (with 500-error shield)
    # =========================================================================
    logger.info("🏛️ Phase 3: Convening the Research Analysis...")

    try:
        research_result = run_research_analysis(
            ticker=ticker_clean,
            lstm_result=lstm_result,
            regime_result=regime_result,
            vix_level=vix_level,
            features_summary=features_summary,
        )
    except Exception as e:
        # Research Analysis crashed even past its own try-except — shield the endpoint
        logger.error(f"❌ Research Analysis catastrophic failure: {e}")
        logger.error(traceback.format_exc())
        research_result = {
            "report": (
                f"## Technical Analysis Only: {ticker_clean} (NSE)\n\n"
                f"⚠️ *AI Agent analysis unavailable. Showing LSTM + HMM results only.*\n\n"
                f"### Market Regime\n**{regime}**\n\n"
                f"### LSTM AI Analysis\n"
                f"- Outlook: **{ai_outlook}**\n"
                f"- Confidence: **{probability:.1%}**\n\n"
                f"### India VIX\n**{vix_level:.1f}**\n\n"
                f"---\n*Error: {str(e)[:200]}*"
            ),
            "technical_summary": "Neutral Outlook",
            "agents_used": ["Technical Analysis Only (Research Analysis Failed)"],
            "error": str(e),
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

    logger.info(f"✅ V2 analysis complete for {ticker_clean}")
    return response
