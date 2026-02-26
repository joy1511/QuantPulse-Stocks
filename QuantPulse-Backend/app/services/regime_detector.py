"""
Regime Detector Service — The Market Weather

Uses a Gaussian Hidden Markov Model (HMM) to classify the current
market regime into one of three states:

- Bull / Stable  (lowest variance state)
- Bear / Volatile (highest variance state)
- Sideways        (middle variance state)

Fits dynamically on Nifty 50 data to capture the current market "weather",
allowing downstream agents to adapt their behavior accordingly.
"""

import logging

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

logger = logging.getLogger(__name__)

# =============================================================================
# Regime Detection
# =============================================================================

def detect_regime(nifty_df: pd.DataFrame) -> dict:
    """
    Detect the current market regime using a 3-state Gaussian HMM.

    Process:
    1. Calculate daily returns and rolling volatility from Nifty 50 data
    2. Fit a GaussianHMM(n_components=3) on [returns, volatility]
    3. Auto-label states by variance:
       - Lowest variance  → "Bull / Stable"
       - Highest variance → "Bear / Volatile"
       - Middle variance  → "Sideways"
    4. Return the CURRENT regime (last observation's hidden state)

    Args:
        nifty_df: DataFrame with Nifty 50 OHLCV data (from data_provider)

    Returns:
        dict with keys:
        - regime: str ("Bull / Stable", "Bear / Volatile", "Sideways")
        - confidence: float (posterior probability of the detected state)
        - state_id: int (0, 1, or 2 — the raw HMM state index)
        - all_states: dict mapping state labels to their properties
    """
    # Fallback if no data
    if nifty_df is None or nifty_df.empty or len(nifty_df) < 60:
        logger.warning("⚠️ Insufficient Nifty data for regime detection, defaulting to Sideways")
        return {
            "regime": "Sideways",
            "confidence": 0.5,
            "state_id": -1,
            "all_states": {},
            "error": "Insufficient data for HMM fitting",
        }

    try:
        close = nifty_df["Close"].astype(float).dropna()

        # Calculate observations
        returns = close.pct_change().dropna()
        volatility = returns.rolling(window=20).std().dropna()

        # Align both series
        common_idx = returns.index.intersection(volatility.index)
        returns = returns.loc[common_idx]
        volatility = volatility.loc[common_idx]

        # Build observation matrix: (n_samples, 2)
        observations = np.column_stack([returns.values, volatility.values])

        if len(observations) < 60:
            logger.warning("⚠️ Not enough aligned observations for HMM")
            return {
                "regime": "Sideways",
                "confidence": 0.5,
                "state_id": -1,
                "all_states": {},
                "error": "Not enough aligned observations",
            }

        # Fit the HMM
        logger.info(f"🔬 Fitting GaussianHMM on {len(observations)} Nifty observations...")
        model = GaussianHMM(
            n_components=3,
            covariance_type="full",
            n_iter=200,
            random_state=42,
            verbose=False,
        )
        model.fit(observations)

        # Predict hidden states
        hidden_states = model.predict(observations)
        state_posteriors = model.predict_proba(observations)

        # Current state = last observation's hidden state
        current_state = int(hidden_states[-1])
        current_confidence = float(state_posteriors[-1][current_state])

        # Auto-label by variance: get the variance (diagonal of covariance)
        # For each state, sum the variances across features
        state_variances = {}
        for i in range(3):
            cov_matrix = model.covars_[i]
            total_var = np.trace(cov_matrix)  # Sum of diagonal = total variance
            state_variances[i] = total_var

        # Sort states by variance
        sorted_states = sorted(state_variances.items(), key=lambda x: x[1])
        # sorted_states[0] = lowest variance (Bull), sorted_states[2] = highest (Bear)

        label_map = {
            sorted_states[0][0]: "Bull / Stable",
            sorted_states[1][0]: "Sideways",
            sorted_states[2][0]: "Bear / Volatile",
        }

        # Build summary of all states
        all_states = {}
        for state_id, label in label_map.items():
            state_mean_return = float(model.means_[state_id][0])
            state_mean_vol = float(model.means_[state_id][1])
            state_var = float(state_variances[state_id])
            # Count how many days in this state
            days_in_state = int(np.sum(hidden_states == state_id))

            all_states[label] = {
                "state_id": state_id,
                "mean_return": round(state_mean_return, 6),
                "mean_volatility": round(state_mean_vol, 6),
                "total_variance": round(state_var, 10),
                "days_in_state": days_in_state,
            }

        current_regime = label_map[current_state]

        logger.info(
            f"🌤️ Regime detected: {current_regime} "
            f"(confidence: {current_confidence:.2%}, "
            f"state_id: {current_state})"
        )

        return {
            "regime": current_regime,
            "confidence": round(current_confidence, 4),
            "state_id": current_state,
            "all_states": all_states,
        }

    except Exception as e:
        logger.error(f"❌ Regime detection failed: {e}")
        return {
            "regime": "Sideways",
            "confidence": 0.5,
            "state_id": -1,
            "all_states": {},
            "error": str(e),
        }
