"""
Regime Detector Service — The Market Weather

Uses a rule-based approach to classify the current market regime into one of three states:

- Bull / Stable:  Positive 30-day returns (>8%) OR moderate positive returns with low volatility
- Bear / Volatile: Negative 30-day returns (<-8%) OR moderate negative returns with high volatility  
- Sideways:       Small returns (-3% to +3%) with any volatility

The rule-based approach is more reliable than HMM which often fails to converge
on real market data. It uses:
- 30-day return trend
- 30-day annualized volatility
- Mean daily returns

This allows downstream agents to adapt their behavior based on current market conditions.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# =============================================================================
# Regime Detection
# =============================================================================

def detect_regime(nifty_df: pd.DataFrame) -> dict:
    """
    Detect the current market regime using a hybrid approach:
    1. Simple rule-based classification (primary)
    2. HMM-based classification (secondary, if converges)
    
    Rule-based approach uses:
    - 30-day return trend
    - 30-day volatility
    - Recent price momentum
    
    This is more reliable than HMM which often fails to converge on real market data.

    Args:
        nifty_df: DataFrame with Nifty 50 OHLCV data (from data_provider)

    Returns:
        dict with keys:
        - regime: str ("Bull / Stable", "Bear / Volatile", "Sideways")
        - confidence: float (confidence in the classification)
        - method: str ("rule_based" or "hmm")
        - all_states: dict with regime statistics
    """
    # Fallback if no data
    if nifty_df is None or nifty_df.empty or len(nifty_df) < 60:
        logger.warning("⚠️ Insufficient Nifty data for regime detection, defaulting to Sideways")
        return {
            "regime": "Sideways",
            "confidence": 0.5,
            "method": "fallback",
            "all_states": {},
            "error": "Insufficient data",
        }

    try:
        close = nifty_df["Close"].astype(float).dropna()
        
        if len(close) < 60:
            logger.warning("⚠️ Not enough data points for regime detection")
            return {
                "regime": "Sideways",
                "confidence": 0.5,
                "method": "fallback",
                "all_states": {},
                "error": "Not enough data points",
            }

        # Calculate returns and volatility
        returns = close.pct_change().dropna()
        
        # =====================================================================
        # RULE-BASED REGIME DETECTION (Primary Method)
        # =====================================================================
        
        # 1. Calculate 30-day metrics
        recent_30d_close = close.iloc[-30:]
        recent_30d_returns = returns.iloc[-30:]
        
        # Total return over last 30 days
        total_return_30d = ((recent_30d_close.iloc[-1] / recent_30d_close.iloc[0]) - 1) * 100
        
        # Volatility (annualized)
        volatility_30d = recent_30d_returns.std() * np.sqrt(252) * 100
        
        # Mean daily return
        mean_return_30d = recent_30d_returns.mean() * 100
        
        # 2. Calculate 90-day metrics for context
        if len(close) >= 90:
            recent_90d_close = close.iloc[-90:]
            total_return_90d = ((recent_90d_close.iloc[-1] / recent_90d_close.iloc[0]) - 1) * 100
        else:
            total_return_90d = total_return_30d
        
        # 3. Classify regime based on rules
        regime = "Sideways"
        confidence = 0.6
        
        # Bear market: significant negative returns OR high volatility with negative trend
        if total_return_30d < -8 or (total_return_30d < -3 and volatility_30d > 25):
            regime = "Bear / Volatile"
            confidence = min(0.95, 0.6 + abs(total_return_30d) / 20)
            
        # Bull market: significant positive returns with moderate volatility
        elif total_return_30d > 8 or (total_return_30d > 3 and volatility_30d < 20):
            regime = "Bull / Stable"
            confidence = min(0.95, 0.6 + total_return_30d / 20)
            
        # Sideways: small returns, any volatility
        else:
            regime = "Sideways"
            # Lower confidence for sideways (it's the default)
            confidence = 0.5 + (1 - abs(total_return_30d) / 10) * 0.2
            confidence = min(0.75, confidence)
        
        logger.info(
            f"🌤️ Regime detected: {regime} "
            f"(confidence: {confidence:.2%}, method: rule_based)"
        )
        logger.info(
            f"   📊 Metrics: 30d return={total_return_30d:.2f}%, "
            f"volatility={volatility_30d:.1f}%, "
            f"mean_daily_return={mean_return_30d:.4f}%"
        )
        
        # Build state summary
        all_states = {
            "Current Regime": {
                "regime": regime,
                "30d_return_pct": round(total_return_30d, 2),
                "90d_return_pct": round(total_return_90d, 2),
                "30d_volatility_annualized": round(volatility_30d, 2),
                "mean_daily_return_pct": round(mean_return_30d, 4),
            }
        }
        
        return {
            "regime": regime,
            "confidence": round(confidence, 4),
            "method": "rule_based",
            "all_states": all_states,
        }

    except Exception as e:
        logger.error(f"❌ Regime detection failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "regime": "Sideways",
            "confidence": 0.5,
            "method": "fallback",
            "all_states": {},
            "error": str(e),
        }
