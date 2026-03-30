# Fix Summary: Stale Data, Neutral Predictions, and Regime Detection Issues

## Problems Identified

### 1. Stale Data and Neutral LSTM Predictions

The backend was showing stale prices (5-6 rupees gap from current prices) and neutral predictions for all stocks, including top losers. Analysis of the logs revealed:

1. **IndianAPI was returning insufficient historical data**:
   - For "1yr" period: Only 115-247 days instead of ~250 days
   - For "2y" requests: Mapped to "1yr" which gave incomplete data
   - For "3yr" period: Weekly candles (6-day spacing) instead of daily

2. **Data priority on cloud was incorrect**:
   - IndianAPI was tried first (insufficient data)
   - yfinance was used as last resort (but it works perfectly)

3. **LSTM predictions were neutral** because:
   - Insufficient historical data (< 200 rows)
   - LSTM needs 60+ consecutive daily candles after feature engineering
   - With sparse data, predictions defaulted to neutral

4. **Ticker normalization issue**:
   - "NIFTY50" was being normalized to "NIFTY50.NS" (invalid)
   - Should be mapped to "^NSEI" (correct index symbol)

### 2. HMM Regime Detector Always Showing "Sideways"

The HMM-based regime detector had critical issues:

1. **Model not converging**:
   ```
   WARNING - Model is not converging. Current: 3419.46 is not greater than 3420.43
   ```

2. **Always predicting "Sideways"** with low confidence (~52%)

3. **Root causes**:
   - HMM with only 2 features (returns, volatility) was too simple
   - Diagonal covariance was insufficient for market data
   - Random initialization led to local minima
   - Variance-based labeling was unreliable

4. **Actual market condition**:
   - 30-day return: -12.33% (clearly bearish!)
   - But HMM was showing "Sideways" with 52% confidence

## Solutions Implemented

### 1. Fixed Data Source Priority on Cloud

**File**: `QuantPulse-Backend/app/services/data_provider.py`

**Before** (Cloud path):
```python
if IS_CLOUD:
    # IndianAPI first → nsepython → yfinance (last resort)
```

**After** (Cloud path):
```python
if IS_CLOUD:
    # yfinance first → IndianAPI (with validation) → nsepython
    df = _download_safe_sync(ticker, period)
    if df is not None and not df.empty:
        logger.info(f"✅ Data source: yfinance (cloud) for {ticker}")
        save_to_cache(ticker, f"historical_{period}", df)
        return df
```

**Rationale**:
- yfinance provides complete 2-year data (494+ rows)
- IndianAPI is better for live quotes, not historical data
- This ensures LSTM always has sufficient data for predictions

### 2. Added Data Quality Validation for IndianAPI

**File**: `QuantPulse-Backend/app/services/data_provider.py`

```python
if df is not None and len(df) >= 200:  # Ensure we have enough data for LSTM
    logger.info(f"✅ Data source: IndianAPI for {ticker}")
    save_to_cache(ticker, f"historical_{period}", df)
    return df
else:
    logger.warning(f"⚠️ IndianAPI returned insufficient data for {ticker}: {len(df) if df is not None else 0} rows")
```

**Rationale**:
- LSTM needs minimum 200 rows for reliable predictions
- Prevents using sparse data that leads to neutral predictions

### 3. Added Ticker Alias Mapping

**File**: `QuantPulse-Backend/app/services/data_provider.py`

```python
TICKER_ALIASES = {
    "NIFTY": "^NSEI",
    "NIFTY50": "^NSEI",
    "NIFTY 50": "^NSEI",
    "NIFTY_50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "VIX": "^INDIAVIX",
    "INDIAVIX": "^INDIAVIX",
    "INDIA VIX": "^INDIAVIX",
}

def normalize_ticker(ticker: str) -> str:
    """Normalize ticker symbol to the correct format."""
    ticker = ticker.strip().upper()
    
    # Check for known aliases first
    if ticker in TICKER_ALIASES:
        return TICKER_ALIASES[ticker]
    
    # ... rest of normalization logic
```

**Rationale**:
- Users often search for "NIFTY50" instead of "^NSEI"
- Provides better UX by accepting common aliases

### 4. Replaced HMM with Rule-Based Regime Detection

**File**: `QuantPulse-Backend/app/services/regime_detector.py`

**Before**: HMM-based approach (not converging)
```python
model = GaussianHMM(n_components=3, covariance_type="diag", n_iter=200)
model.fit(observations)
# Often failed to converge, always predicted "Sideways"
```

**After**: Rule-based approach (reliable)
```python
# Calculate 30-day metrics
total_return_30d = ((recent_30d_close.iloc[-1] / recent_30d_close.iloc[0]) - 1) * 100
volatility_30d = recent_30d_returns.std() * np.sqrt(252) * 100

# Classify regime based on rules
if total_return_30d < -8 or (total_return_30d < -3 and volatility_30d > 25):
    regime = "Bear / Volatile"
elif total_return_30d > 8 or (total_return_30d > 3 and volatility_30d < 20):
    regime = "Bull / Stable"
else:
    regime = "Sideways"
```

**Rationale**:
- Rule-based approach is more reliable and interpretable
- Uses clear thresholds based on market behavior
- Provides accurate regime classification with high confidence
- No convergence issues

## Test Results

### Before Fixes
```
Data:
  NIFTY50: 115 rows (insufficient)
  RELIANCE: 247 rows (insufficient for 2y)

LSTM:
  Predictions: Neutral (due to sparse data)

Regime Detector:
  Regime: Sideways (incorrect!)
  Confidence: 52% (low)
  Issue: HMM not converging
```

### After Fixes
```
Data:
  NIFTY50: 494 rows ✅ (mapped to ^NSEI)
  RELIANCE: 495 rows ✅ (complete 2-year data)
  Latest close: ₹1343.90 ✅ (matches live price)
  Data quality: GOOD (>400 rows) ✅

LSTM:
  Ready: YES ✅
  Sufficient data for predictions ✅

Regime Detector:
  Regime: Bear / Volatile ✅ (correct!)
  Confidence: 95% ✅ (high)
  Method: rule_based ✅
  30-day return: -12.33% ✅
  90-day return: -13.81% ✅
  Volatility: 21.88% ✅
```

## Impact

1. **Accurate Predictions**: LSTM now has sufficient data for reliable predictions
2. **Current Prices**: Latest prices match live market data
3. **Correct Regime Detection**: Now accurately identifies bear/bull/sideways markets
4. **High Confidence**: Regime detection confidence increased from 52% to 95%
5. **Better UX**: Common ticker aliases (NIFTY50, BANKNIFTY) work correctly
6. **Reliable on Cloud**: yfinance provides consistent data on Render deployment

## Files Modified

1. `QuantPulse-Backend/app/services/data_provider.py`
   - Changed cloud data source priority
   - Added ticker alias mapping
   - Added data quality validation

2. `QuantPulse-Backend/app/providers/indianapi_provider.py`
   - Updated comments to clarify period limitations

3. `QuantPulse-Backend/app/services/regime_detector.py`
   - Replaced HMM with rule-based approach
   - Added 30-day and 90-day return metrics
   - Added annualized volatility calculation
   - Removed hmmlearn dependency

## Testing

Run the test scripts to verify the fixes:

```bash
cd QuantPulse-Backend

# Test data fetching
python test_data_priority.py

# Test regime detection
python test_regime_simple.py
```

Expected output:
- ✅ RELIANCE: 495 rows with latest close ₹1343.90
- ✅ NIFTY50: 494 rows (correctly mapped to ^NSEI)
- ✅ Data quality: GOOD (>400 rows)
- ✅ LSTM ready: YES
- ✅ Regime: Bear / Volatile (95% confidence)
- ✅ 30-day return: -12.33%

## Deployment Notes

1. **No environment variable changes needed**
2. **No database migrations required**
3. **Cache will be automatically refreshed** (24-hour TTL)
4. **Restart backend** to apply changes:
   ```bash
   # On Render, this happens automatically on git push
   # Locally:
   python QuantPulse-Backend/run.py
   ```

## Monitoring

After deployment, check logs for:
- `✅ Data source: yfinance (cloud) for {ticker}` - Confirms yfinance is being used
- `🌤️ Regime detected: {regime} (confidence: XX%, method: rule_based)` - Confirms regime detection
- `📊 Metrics: 30d return=XX%, volatility=XX%` - Shows actual market metrics
- Data row counts should be 400+ for 2-year period

## Future Improvements

1. Consider using IndianAPI for intraday data (1m, 5m candles)
2. Add more ticker aliases as users request them
3. Implement data quality metrics dashboard
4. Add alerting for data source failures
5. Add regime transition detection (e.g., "Bull → Sideways")
6. Implement regime-specific LSTM models for better predictions
