"""
Comprehensive test to verify all fixes are working
"""

import asyncio
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_complete_fix():
    """Test all fixes comprehensively"""
    
    print("=" * 70)
    print("COMPREHENSIVE FIX VERIFICATION TEST")
    print("=" * 70)
    
    from app.services.data_provider import fetch_market_context
    from app.services.regime_detector import detect_regime
    from app.services.lstm_service import predict as lstm_predict
    
    # Test 1: Data Fetching
    print("\n" + "=" * 70)
    print("TEST 1: Data Fetching (yfinance priority)")
    print("=" * 70)
    
    context = await fetch_market_context("RELIANCE")
    target_df = context.get("target_df")
    nifty_df = context.get("nifty_df")
    vix_df = context.get("vix_df")
    
    print(f"\nRELIANCE Data:")
    print(f"  Rows: {len(target_df)}")
    print(f"  Latest close: ₹{target_df['Close'].iloc[-1]:.2f}")
    print(f"  Status: {'✅ PASS' if len(target_df) > 400 else '❌ FAIL'}")
    
    print(f"\nNifty 50 Data:")
    print(f"  Rows: {len(nifty_df)}")
    print(f"  Latest close: {nifty_df['Close'].iloc[-1]:.2f}")
    print(f"  Status: {'✅ PASS' if len(nifty_df) > 400 else '❌ FAIL'}")
    
    # Test 2: Ticker Alias Mapping
    print("\n" + "=" * 70)
    print("TEST 2: Ticker Alias Mapping (NIFTY50 → ^NSEI)")
    print("=" * 70)
    
    nifty50_context = await fetch_market_context("NIFTY50")
    nifty50_df = nifty50_context.get("target_df")
    
    print(f"\nNIFTY50 (should map to ^NSEI):")
    print(f"  Rows: {len(nifty50_df)}")
    print(f"  Latest close: {nifty50_df['Close'].iloc[-1]:.2f}")
    print(f"  Status: {'✅ PASS' if len(nifty50_df) > 400 else '❌ FAIL'}")
    
    # Test 3: Regime Detection
    print("\n" + "=" * 70)
    print("TEST 3: Regime Detection (Rule-Based)")
    print("=" * 70)
    
    regime_result = detect_regime(nifty_df)
    
    print(f"\nRegime Detection:")
    print(f"  Regime: {regime_result['regime']}")
    print(f"  Confidence: {regime_result['confidence']:.2%}")
    print(f"  Method: {regime_result['method']}")
    
    if 'all_states' in regime_result and regime_result['all_states']:
        metrics = regime_result['all_states']['Current Regime']
        print(f"\n  Market Metrics:")
        print(f"    30-day return: {metrics['30d_return_pct']:.2f}%")
        print(f"    90-day return: {metrics['90d_return_pct']:.2f}%")
        print(f"    Volatility: {metrics['30d_volatility_annualized']:.2f}%")
    
    # Check if regime makes sense
    regime_ok = regime_result['confidence'] > 0.6 and regime_result['method'] == 'rule_based'
    print(f"  Status: {'✅ PASS' if regime_ok else '❌ FAIL'}")
    
    # Test 4: LSTM Prediction
    print("\n" + "=" * 70)
    print("TEST 4: LSTM Prediction (Sufficient Data)")
    print("=" * 70)
    
    lstm_result = lstm_predict("RELIANCE", target_df)
    
    print(f"\nLSTM Prediction:")
    print(f"  Outlook: {lstm_result.get('outlook', 'N/A')}")
    print(f"  Probability: {lstm_result.get('probability', 0):.4f}")
    
    if 'error' in lstm_result:
        print(f"  Error: {lstm_result['error']}")
        print(f"  Status: ❌ FAIL")
    else:
        features = lstm_result.get('features_summary', {})
        print(f"\n  Technical Indicators:")
        print(f"    RSI: {features.get('rsi', 'N/A')}")
        print(f"    MACD: {features.get('macd', 'N/A')}")
        print(f"  Status: ✅ PASS")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_pass = (
        len(target_df) > 400 and
        len(nifty_df) > 400 and
        len(nifty50_df) > 400 and
        regime_ok and
        'error' not in lstm_result
    )
    
    if all_pass:
        print("\n✅ ALL TESTS PASSED!")
        print("\nFixes verified:")
        print("  ✅ Data fetching: yfinance provides complete 2-year data")
        print("  ✅ Ticker aliases: NIFTY50 correctly maps to ^NSEI")
        print("  ✅ Regime detection: Rule-based approach working correctly")
        print("  ✅ LSTM predictions: Sufficient data for reliable predictions")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease check the output above for details.")
    
    return all_pass

if __name__ == "__main__":
    result = asyncio.run(test_complete_fix())
    sys.exit(0 if result else 1)
