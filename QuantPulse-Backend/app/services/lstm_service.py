"""
LSTM Prediction Service — The Neural Predictor

Loads the pre-trained Universal LSTM model and scaler to generate
buy/sell/neutral signals for any NSE stock.

Feature Engineering matches the training script exactly:
1. Log Returns
2. RSI (14) via EWMA
3. MACD (12, 26)
4. Volatility (20-day rolling std of log returns)
5. Bollinger %B (20-day, 2-std)
6. Normalized ATR (14-period ATR / Close)

Uses the last 60 time steps as input window.
"""

import os
import logging

import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

# =============================================================================
# Global Model Loading (downloads from Hugging Face on first run)
# =============================================================================

_MODEL = None
_SCALER = None

HF_REPO_ID = "joy1511/QuantPulse-Models"


def _build_model():
    """
    Build the LSTM model architecture in code.
    This is version-independent — no Keras serialization needed.

    Architecture (matches training script):
      Input(60, 6) → BiLSTM(64, seq=True) → BN → Drop(0.3)
                    → BiLSTM(64, seq=False) → BN → Drop(0.3)
                    → Dense(32, relu) → Drop(0.2) → Dense(1, sigmoid)
    """
    import tensorflow as tf

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(60, 6)),
        tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(64, return_sequences=True)
        ),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(64, return_sequences=False)
        ),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    return model


def _load_model():
    """Download model weights from Hugging Face, build architecture, load weights."""
    global _MODEL, _SCALER

    try:
        from huggingface_hub import hf_hub_download
        from app.config import HF_TOKEN

        token = HF_TOKEN

        logger.info(f"📥 Downloading LSTM weights from Hugging Face ({HF_REPO_ID})...")
        weights_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename="universal_lstm.weights.h5",
            token=token
        )
        logger.info(f"✅ Weights downloaded to: {weights_path}")

        logger.info(f"📥 Downloading scaler from Hugging Face ({HF_REPO_ID})...")
        scaler_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename="universal_scaler.pkl",
            token=token
        )
        logger.info(f"✅ Scaler downloaded to: {scaler_path}")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"CRITICAL: Model Download Failed")
        print(f"Could not download from Hugging Face ({HF_REPO_ID})")
        print(f"Error: {e}")
        print(f"The LSTM predictor will return Neutral for all tickers.")
        print(f"{'='*60}\n")
        logger.error(f"❌ CRITICAL: Model download failed: {e}")
        return

    try:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")

        logger.info(f"🧠 Building LSTM architecture and loading weights...")
        _MODEL = _build_model()
        _MODEL.load_weights(weights_path)
        logger.info(f"✅ LSTM model ready: input_shape={_MODEL.input_shape}")

        logger.info(f"📏 Loading scaler...")
        _SCALER = joblib.load(scaler_path)
        logger.info(f"✅ Scaler loaded: {type(_SCALER).__name__}")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"CRITICAL: Model Loading Failed (files downloaded but cannot load)")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"❌ CRITICAL: Model load failed after download: {e}")


def init():
    """Public initializer — called from main.py startup event, NOT at import time.
    This lets uvicorn bind the port FIRST, then loads TF + model weights."""
    _load_model()


# =============================================================================
# Manual Feature Engineering (matches training script exactly)
# =============================================================================

def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate exactly 6 technical features from OHLCV data.
    Uses only pandas/numpy math — NO pandas-ta.

    Args:
        df: DataFrame with columns: Open, High, Low, Close, Volume

    Returns:
        DataFrame with 6 feature columns, NaN rows dropped.
    """
    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)

    features = pd.DataFrame(index=df.index)

    # 1. Log Returns: ln(Close_t / Close_{t-1})
    features["log_return"] = np.log(close / close.shift(1))

    # 2. RSI (14) via EWMA (com=13, which is equivalent to span=27... 
    #    but the standard RSI convention with com=13 gives span=14 adjustment)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=13, min_periods=14).mean()
    avg_loss = loss.ewm(com=13, min_periods=14).mean()
    rs = avg_gain / avg_loss
    features["rsi"] = 100 - (100 / (1 + rs))

    # 3. MACD: EMA(12) - EMA(26)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    features["macd"] = ema12 - ema26

    # 4. Volatility: 20-day rolling std dev of log returns
    features["volatility"] = features["log_return"].rolling(window=20).std()

    # 5. Bollinger %B: (Close - LowerBB) / (UpperBB - LowerBB)
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    upper_bb = sma20 + 2 * std20
    lower_bb = sma20 - 2 * std20
    bb_width = upper_bb - lower_bb
    features["bollinger_pctb"] = np.where(
        bb_width != 0,
        (close - lower_bb) / bb_width,
        0.5  # Default to midpoint if bands are flat
    )

    # 6. Normalized ATR: ATR(14) / Close
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr14 = tr.rolling(window=14).mean()
    features["norm_atr"] = atr14 / close

    # Drop NaN rows created by rolling calculations
    features.dropna(inplace=True)

    return features


# =============================================================================
# Prediction Inference
# =============================================================================

def predict(ticker: str, target_df: pd.DataFrame = None) -> dict:
    """
    Run LSTM inference for a given stock ticker.

    Process:
    1. Validate / Fetch live data (target_df must be provided)
    2. Engineer 6 features
    3. Take last 60 rows, scale, reshape to (1, 60, 6)
    4. Run model.predict()
    5. Return probability and signal

    Args:
        ticker: Stock symbol (e.g., "RELIANCE")
        target_df: Pre-fetched market data (Open, High, Low, Close, Volume)
                   If None, returns error (no internal fetching to avoid async issues).

    Returns:
        dict with keys:
        - probability: float (0-1, where >0.5 = bullish)
        - signal: "Buy" | "Sell" | "Neutral"
        - features_summary: dict with latest feature values
    """
    # Lazy loading: Load model on first prediction request
    global _MODEL, _SCALER
    if _MODEL is None or _SCALER is None:
        logger.info("🧠 First prediction request - loading LSTM model...")
        _load_model()
    
    if _MODEL is None or _SCALER is None:
        return {
            "probability": 0.5,
            "outlook": "Neutral Outlook",
            "error": "Model not loaded. Check models/ directory.",
            "features_summary": {},
        }

    # Step 1: Use provided data
    if target_df is None or target_df.empty:
        return {
            "probability": 0.5,
            "outlook": "Neutral Outlook",
            "error": f"No market data provided for {ticker}",
            "features_summary": {},
        }

    # Step 2: Engineer features
    features_df = calculate_features(target_df)

    if len(features_df) < 60:
        return {
            "probability": 0.5,
            "outlook": "Neutral Outlook",
            "error": f"Insufficient data: need 60 rows, got {len(features_df)}",
            "features_summary": {},
        }

    # Step 3: Take last 60 rows
    window = features_df.iloc[-60:].values  # shape: (60, 6)

    # Step 4: Scale using the loaded scaler
    window_scaled = _SCALER.transform(window)  # shape: (60, 6)

    # Step 5: Reshape for LSTM input: (batch_size, time_steps, features)
    X = window_scaled.reshape(1, 60, 6)

    # Step 6: Predict
    raw_pred = _MODEL.predict(X, verbose=0)
    probability = float(raw_pred[0][0])

    # Step 7: Classify outlook (research-based, not trading advice)
    if probability > 0.55:
        outlook = "Bullish Outlook"
    elif probability < 0.45:
        outlook = "Bearish Outlook"
    else:
        outlook = "Neutral Outlook"

    # Build features summary (latest values for the frontend / agents)
    latest = features_df.iloc[-1]
    features_summary = {
        "rsi": round(float(latest["rsi"]), 2),
        "macd": round(float(latest["macd"]), 4),
        "volatility": round(float(latest["volatility"]), 6),
        "bollinger_pctb": round(float(latest["bollinger_pctb"]), 4),
        "norm_atr": round(float(latest["norm_atr"]), 6),
    }

    logger.info(
        f"🧠 LSTM Analysis for {ticker}: "
        f"P={probability:.4f} → {outlook} | "
        f"RSI={features_summary['rsi']}, MACD={features_summary['macd']}"
    )

    return {
        "probability": round(probability, 4),
        "outlook": outlook,
        "features_summary": features_summary,
    }
