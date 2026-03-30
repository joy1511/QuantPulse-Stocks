"""Simple test for regime detector"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test():
    from app.services.data_provider import fetch_market_context
    from app.services.regime_detector import detect_regime
    
    print("Fetching data...")
    context = await fetch_market_context("RELIANCE")
    nifty_df = context.get("nifty_df")
    
    print(f"Nifty data: {len(nifty_df)} rows")
    
    print("\nDetecting regime...")
    result = detect_regime(nifty_df)
    
    print(f"\nResult:")
    print(f"  Regime: {result['regime']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Method: {result['method']}")
    
    if 'all_states' in result and result['all_states']:
        print(f"\n  Metrics:")
        for key, value in result['all_states']['Current Regime'].items():
            print(f"    {key}: {value}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test())
