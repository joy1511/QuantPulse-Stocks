"""
AI Prediction Router

This module provides a prototype AI prediction endpoint that combines:
1. Technical analysis (price trends, moving averages) - PRIMARY SIGNAL
2. News sentiment analysis - MODIFIER SIGNAL

IMPORTANT DISCLAIMER:
This is a PROTOTYPE implementation for demonstration purposes only.
It should NOT be used for actual trading decisions.
Past performance and technical patterns do not guarantee future results.

=============================================================================
PREDICTION LOGIC - TRANSPARENT AND EXPLAINABLE
=============================================================================

RULE 1: Direction is determined PRIMARILY by technical trend
-----------------------------------------------------------------
- Technical analysis (price vs moving average) determines UP/DOWN direction
- News sentiment does NOT flip the direction
- This ensures predictions are grounded in actual price movement

RULE 2: News sentiment STRENGTHENS or WEAKENS the trend
-----------------------------------------------------------------
- Positive news + UP trend = Stronger bullish signal
- Negative news + UP trend = Weaker bullish signal (but still UP)
- Positive news + DOWN trend = Weaker bearish signal (but still DOWN)
- Negative news + DOWN trend = Stronger bearish signal

RULE 3: Trend labels based on signal agreement
-----------------------------------------------------------------
- "Bullish" / "Bearish": Technical and news signals AGREE
- "Neutral": Signals CONFLICT or technical trend is weak (sideways)
- "Strong Bullish/Bearish": High confidence with agreement

RULE 4: Confidence calculation (weighted average)
-----------------------------------------------------------------
overallConfidence = (technicalConfidence × 0.7) + (newsConfidence × 0.3)

Technical analysis gets 70% weight because:
- It's based on actual price data
- More reliable short-term indicator
- Less susceptible to noise

News sentiment gets 30% weight because:
- It's a supporting/contextual signal
- Helps capture market sentiment not in price yet
- Can strengthen or weaken technical signals

=============================================================================
"""

from fastapi import APIRouter, HTTPException, Path
from datetime import datetime
import yfinance as yf
import httpx
import asyncio
from typing import Optional

# Create router for AI prediction endpoints
router = APIRouter(
    prefix="/ai-prediction",
    tags=["AI Predictions"],
)

# =============================================================================
# Configuration
# =============================================================================

# Weights for combining confidence scores
TECHNICAL_WEIGHT = 0.7
NEWS_WEIGHT = 0.3

# Moving average period (in days)
MA_PERIOD = 5

# Internal API base URL
INTERNAL_API_BASE = "http://localhost:8000"


# =============================================================================
# Technical Analysis Functions
# =============================================================================

def fetch_historical_prices(symbol: str, period: str = "1mo") -> list:
    """
    Fetch historical price data from Yahoo Finance.
    Blocking I/O - should be run in a thread.
    """
    yf_symbol = f"{symbol.upper()}.NS"
    
    try:
        ticker = yf.Ticker(yf_symbol)
        history = ticker.history(period=period)
        
        if history.empty:
            return []
        
        return history['Close'].tolist()
        
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []


def get_current_price_info(symbol: str) -> dict:
    """
    Fetch current price info from Yayoo Finance.
    Blocking I/O - should be run in a thread.
    """
    yf_symbol = f"{symbol.upper()}.NS"
    try:
        ticker = yf.Ticker(yf_symbol)
        return ticker.info
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return {}


def calculate_sma(prices: list, period: int) -> Optional[float]:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return None
    recent_prices = prices[-period:]
    return sum(recent_prices) / period


def calculate_technical_signal(current_price: float, sma: float) -> dict:
    """Calculate technical signal based on price vs moving average."""
    deviation_percent = ((current_price - sma) / sma) * 100
    
    if deviation_percent > 0.5:
        direction = "UP"
        trend_label = "Bullish"
    elif deviation_percent < -0.5:
        direction = "DOWN"
        trend_label = "Bearish"
    else:
        direction = "SIDEWAYS"
        trend_label = "Neutral"
    
    abs_deviation = abs(deviation_percent)
    if abs_deviation < 1:
        confidence = 30 + (abs_deviation * 20)
    elif abs_deviation < 3:
        confidence = 50 + ((abs_deviation - 1) * 10)
    else:
        confidence = 70 + min((abs_deviation - 3) * 5, 20)
    
    confidence = min(confidence, 90)
    
    return {
        "direction": direction,
        "trendLabel": trend_label,
        "technicalConfidence": round(confidence),
        "deviationPercent": round(deviation_percent, 2),
        "currentPrice": round(current_price, 2),
        "sma": round(sma, 2),
    }


# =============================================================================
# Signal Combination Functions
# =============================================================================

def get_news_sentiment_direction(sentiment_label: str) -> str:
    """Convert news sentiment label to a directional indicator."""
    positive_sentiments = ["Very Good", "Good"]
    negative_sentiments = ["Bad", "Very Bad"]
    
    if sentiment_label in positive_sentiments:
        return "POSITIVE"
    elif sentiment_label in negative_sentiments:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


def combine_signals(
    technical_direction: str,
    technical_confidence: int,
    news_sentiment_label: str,
    news_confidence: int
) -> dict:
    """Combine technical and news signals to generate final prediction."""
    
    final_direction = technical_direction
    news_sentiment_direction = get_news_sentiment_direction(news_sentiment_label)
    
    if news_sentiment_direction == "NEUTRAL":
        signals_agree = False
        signals_conflict = False
        agreement_status = "neutral"
    elif technical_direction == "UP":
        signals_agree = (news_sentiment_direction == "POSITIVE")
        signals_conflict = (news_sentiment_direction == "NEGATIVE")
        agreement_status = "agree" if signals_agree else ("conflict" if signals_conflict else "neutral")
    elif technical_direction == "DOWN":
        signals_agree = (news_sentiment_direction == "NEGATIVE")
        signals_conflict = (news_sentiment_direction == "POSITIVE")
        agreement_status = "agree" if signals_agree else ("conflict" if signals_conflict else "neutral")
    else:
        signals_agree = False
        signals_conflict = False
        agreement_status = "neutral"
    
    if technical_direction == "SIDEWAYS":
        trend_label = "Neutral"
    elif signals_conflict:
        if technical_direction == "UP":
            trend_label = "Weak Bullish"
        else:
            trend_label = "Weak Bearish"
    elif signals_agree:
        if technical_direction == "UP":
            trend_label = "Bullish"
        else:
            trend_label = "Bearish"
    else:
        if technical_direction == "UP":
            trend_label = "Bullish"
        else:
            trend_label = "Bearish"
    
    base_confidence = (
        technical_confidence * TECHNICAL_WEIGHT +
        news_confidence * NEWS_WEIGHT
    )
    
    if signals_agree:
        confidence_adjustment = 5
    elif signals_conflict:
        confidence_adjustment = -10 * (news_confidence / 100)
    else:
        confidence_adjustment = 0
    
    overall_confidence = base_confidence + confidence_adjustment
    overall_confidence = max(10, min(95, overall_confidence))
    
    return {
        "finalDirection": final_direction,
        "finalTrendLabel": trend_label,
        "overallConfidence": round(overall_confidence),
        "signalsAgree": signals_agree,
        "signalsConflict": signals_conflict,
        "agreementStatus": agreement_status,
        "technicalDirection": technical_direction,
        "newsSentimentDirection": news_sentiment_direction,
    }


# =============================================================================
# Main Endpoint
# =============================================================================

@router.get("/{symbol}")
async def get_ai_prediction(
    symbol: str = Path(..., pattern=r"^[A-Z0-9\.]+$", description="NSE stock symbol")
):
    """
    Generate AI prediction for a stock by combining technical and news analysis.
    """
    symbol = symbol.upper()
    
    try:
        # =====================================================================
        # Step 1: Fetch current stock data (Blocking -> Thread)
        # =====================================================================
        info = await asyncio.to_thread(get_current_price_info, symbol)
        
        current_price = info.get("regularMarketPrice")
        if not current_price:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch price data for {symbol}"
            )
        
        # =====================================================================
        # Step 2: Fetch historical prices and calculate SMA (Blocking -> Thread)
        # =====================================================================
        prices = await asyncio.to_thread(fetch_historical_prices, symbol)
        
        if len(prices) < MA_PERIOD:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data for {symbol}"
            )
        
        sma = calculate_sma(prices, MA_PERIOD)
        
        # =====================================================================
        # Step 3: Calculate technical signal
        # =====================================================================
        technical_result = calculate_technical_signal(current_price, sma)
        
        # =====================================================================
        # Step 4: Fetch news sentiment (Async HTTP)
        # =====================================================================
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{INTERNAL_API_BASE}/news-sentiment/{symbol}",
                    timeout=30.0
                )
                if response.status_code == 200:
                    news_data = response.json()
                    news_sentiment_label = news_data.get("sentimentLabel", "Neutral")
                    news_confidence = news_data.get("newsConfidence", 50)
                    articles_analyzed = news_data.get("articlesAnalyzed", 0)
                else:
                    # Fallback
                    news_sentiment_label = "Neutral"
                    news_confidence = 50
                    articles_analyzed = 0
        except Exception as e:
            print(f"Error fetching news sentiment: {e}")
            news_sentiment_label = "Neutral"
            news_confidence = 50
            articles_analyzed = 0
        
        # =====================================================================
        # Step 5: Combine signals
        # =====================================================================
        combined = combine_signals(
            technical_direction=technical_result["direction"],
            technical_confidence=technical_result["technicalConfidence"],
            news_sentiment_label=news_sentiment_label,
            news_confidence=news_confidence,
        )
        
        # =====================================================================
        # Step 6: Build response
        # =====================================================================
        
        explanation_lines = [
            f"TECHNICAL (70% weight): Price ₹{technical_result['currentPrice']:.2f} is {abs(technical_result['deviationPercent']):.1f}% {'above' if technical_result['deviationPercent'] > 0 else 'below'} the 5-day SMA (₹{technical_result['sma']:.2f})",
            f"NEWS (30% weight): Sentiment is '{news_sentiment_label}' based on {articles_analyzed} articles → {combined['newsSentimentDirection']} signal",
        ]
        
        if combined["signalsAgree"]:
            explanation_lines.append(f"COMBINATION: Signals AGREE → {combined['finalTrendLabel']} with {combined['overallConfidence']}% confidence")
        elif combined["signalsConflict"]:
            explanation_lines.append(f"COMBINATION: Signals CONFLICT → Direction from technical, reduced confidence ({combined['overallConfidence']}%)")
        else:
            explanation_lines.append(f"COMBINATION: News is NEUTRAL → Using technical direction with {combined['overallConfidence']}% confidence")
        
        response = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "prediction": {
                "direction": combined["finalDirection"],
                "trendLabel": combined["finalTrendLabel"],
                "overallConfidence": combined["overallConfidence"],
                "signalsAgree": combined["signalsAgree"],
                "signalsConflict": combined["signalsConflict"],
                "agreementStatus": combined["agreementStatus"],
            },
            "technical": {
                "direction": technical_result["direction"],
                "trendLabel": technical_result["trendLabel"],
                "confidence": technical_result["technicalConfidence"],
                "weight": "70%",
                "currentPrice": technical_result["currentPrice"],
                "sma5Day": technical_result["sma"],
                "deviationPercent": technical_result["deviationPercent"],
            },
            "news": {
                "sentimentLabel": news_sentiment_label,
                "sentimentDirection": combined["newsSentimentDirection"],
                "confidence": news_confidence,
                "weight": "30%",
                "articlesAnalyzed": articles_analyzed,
            },
            "explanation": explanation_lines,
            "logic": {
                "rule1": "Direction determined by technical analysis (price vs 5-day SMA)",
                "rule2": "News sentiment strengthens or weakens trend, does NOT flip direction",
                "rule3": "Trend label reflects agreement: Bullish/Bearish (agree) or Weak/Neutral (conflict)",
                "rule4": "Confidence = (Technical × 0.7) + (News × 0.3) ± adjustment",
            },
            "disclaimer": "This is a prototype AI prediction for demonstration purposes only. It should NOT be used for actual trading decisions. Past patterns do not guarantee future results.",
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating prediction for {symbol}: {e}")
        # HIDE INTERNAL ERRORS
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction for {symbol}."
        )


@router.get("/test/mock")
async def get_mock_prediction():
    """Test endpoint that returns mock prediction data."""
    return {
        "symbol": "RELIANCE",
        "timestamp": datetime.now().isoformat(),
        "prediction": {
            "direction": "UP",
            "trendLabel": "Bullish",
            "overallConfidence": 74,
            "signalsAgree": True,
            "signalsConflict": False,
            "agreementStatus": "agree",
        },
        "technical": {
            "direction": "UP",
            "trendLabel": "Bullish",
            "confidence": 82,
            "weight": "70%",
            "currentPrice": 2485.30,
            "sma5Day": 2450.15,
            "deviationPercent": 1.43,
        },
        "news": {
            "sentimentLabel": "Good",
            "sentimentDirection": "POSITIVE",
            "confidence": 50,
            "weight": "30%",
            "articlesAnalyzed": 12,
        },
        "explanation": [
            "TECHNICAL (70% weight): Price ₹2485.30 is 1.4% above the 5-day SMA (₹2450.15)",
            "NEWS (30% weight): Sentiment is 'Good' based on 12 articles → POSITIVE signal",
            "COMBINATION: Signals AGREE → Bullish with 74% confidence",
        ],
        "logic": {
            "rule1": "Direction determined by technical analysis (price vs 5-day SMA)",
            "rule2": "News sentiment strengthens or weakens trend, does NOT flip direction",
            "rule3": "Trend label reflects agreement: Bullish/Bearish (agree) or Weak/Neutral (conflict)",
            "rule4": "Confidence = (Technical × 0.7) + (News × 0.3) ± adjustment",
        },
        "disclaimer": "This is mock data for testing purposes.",
    }

