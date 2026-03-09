"""
Test IndianAPI.in Integration with API Key

This script tests:
1. API key loading from config
2. IndianAPI provider initialization
3. Real API calls to IndianAPI.in
4. Stock quote fetching
5. Historical data fetching
6. Company profile fetching
"""

import asyncio
import sys
import os

print("=" * 60)
print("Testing IndianAPI.in Integration")
print("=" * 60)

# Test 1: Load configuration
print("\n1. Loading configuration...")
try:
    from app.config import INDIANAPI_KEY
    
    if INDIANAPI_KEY:
        # Mask the key for security (show first 8 and last 4 characters)
        masked_key = f"{INDIANAPI_KEY[:8]}...{INDIANAPI_KEY[-4:]}" if len(INDIANAPI_KEY) > 12 else "***"
        print(f"✅ INDIANAPI_KEY loaded: {masked_key}")
        print(f"   Key length: {len(INDIANAPI_KEY)} characters")
        print(f"   Tier: Premium (API key provided)")
    else:
        print("ℹ️ INDIANAPI_KEY not set - using FREE tier")
        print("   Tier: FREE (no API key)")
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
    sys.exit(1)

# Test 2: Initialize IndianAPI provider
print("\n2. Initializing IndianAPI provider...")
try:
    from app.providers.indianapi_provider import IndianAPIProvider
    
    provider = IndianAPIProvider(api_key=INDIANAPI_KEY)
    print(f"✅ Provider initialized successfully")
    print(f"   Provider name: {provider.provider_name}")
    print(f"   Base URL: {provider.BASE_URL}")
    print(f"   Has API key: {bool(provider.api_key)}")
except Exception as e:
    print(f"❌ Provider initialization failed: {e}")
    sys.exit(1)

# Test 3: Test API connection with stock quote
print("\n3. Testing stock quote API call...")
async def test_stock_quote():
    try:
        provider = IndianAPIProvider(api_key=INDIANAPI_KEY)
        
        # Test with RELIANCE (major NSE stock)
        print("   Fetching quote for RELIANCE...")
        quote = await provider.get_stock_quote("RELIANCE")
        
        print(f"✅ Stock quote fetched successfully!")
        print(f"   Symbol: {quote.symbol}")
        print(f"   Price: ₹{quote.price}")
        print(f"   Change: ₹{quote.change} ({quote.percent_change}%)")
        print(f"   Volume: {quote.volume:,}")
        print(f"   Exchange: {quote.exchange}")
        print(f"   Currency: {quote.currency}")
        print(f"   Is Demo: {quote.is_demo}")
        
        await provider.close()
        return True
    except Exception as e:
        print(f"❌ Stock quote test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

try:
    result = asyncio.run(test_stock_quote())
    if not result:
        print("\n⚠️ Stock quote test failed - continuing with other tests...")
except Exception as e:
    print(f"❌ Async test failed: {e}")

# Test 4: Test historical data API call
print("\n4. Testing historical data API call...")
async def test_historical_data():
    try:
        provider = IndianAPIProvider(api_key=INDIANAPI_KEY)
        
        # Test with TCS (major NSE stock)
        print("   Fetching 1-year historical data for TCS...")
        historical = await provider.get_historical_data("TCS", period="1y")
        
        print(f"✅ Historical data fetched successfully!")
        print(f"   Symbol: {historical.symbol}")
        print(f"   Period: {historical.period}")
        print(f"   Data points: {len(historical.data)}")
        print(f"   Is Demo: {historical.is_demo}")
        
        if historical.data:
            # Show first and last data point
            first = historical.data[0]
            last = historical.data[-1]
            print(f"   First date: {first.get('date')}")
            print(f"   First close: ₹{first.get('close')}")
            print(f"   Last date: {last.get('date')}")
            print(f"   Last close: ₹{last.get('close')}")
        
        await provider.close()
        return True
    except Exception as e:
        print(f"❌ Historical data test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

try:
    result = asyncio.run(test_historical_data())
    if not result:
        print("\n⚠️ Historical data test failed - continuing with other tests...")
except Exception as e:
    print(f"❌ Async test failed: {e}")

# Test 5: Test company profile API call
print("\n5. Testing company profile API call...")
async def test_company_profile():
    try:
        provider = IndianAPIProvider(api_key=INDIANAPI_KEY)
        
        # Test with INFY (major NSE stock)
        print("   Fetching company profile for INFY...")
        profile = await provider.get_company_profile("INFY")
        
        print(f"✅ Company profile fetched successfully!")
        print(f"   Symbol: {profile.symbol}")
        print(f"   Name: {profile.name}")
        print(f"   Sector: {profile.sector}")
        print(f"   Industry: {profile.industry}")
        print(f"   Market Cap: {profile.market_cap_formatted}")
        print(f"   Is Demo: {profile.is_demo}")
        
        if profile.description:
            desc_preview = profile.description[:100] + "..." if len(profile.description) > 100 else profile.description
            print(f"   Description: {desc_preview}")
        
        await provider.close()
        return True
    except Exception as e:
        print(f"❌ Company profile test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

try:
    result = asyncio.run(test_company_profile())
    if not result:
        print("\n⚠️ Company profile test failed")
except Exception as e:
    print(f"❌ Async test failed: {e}")

# Test 6: Test data provider integration
print("\n6. Testing data provider integration...")
async def test_data_provider():
    try:
        from app.services.data_provider import _indianapi_provider, INDIANAPI_AVAILABLE
        
        if not INDIANAPI_AVAILABLE:
            print("❌ IndianAPI provider not available in data_provider")
            return False
        
        print(f"✅ IndianAPI provider available in data_provider")
        print(f"   Provider initialized: {_indianapi_provider is not None}")
        
        if _indianapi_provider:
            print(f"   Has API key: {bool(_indianapi_provider.api_key)}")
            
            # Test a quick quote fetch through data provider
            print("   Testing quote fetch through data provider...")
            quote = await _indianapi_provider.get_stock_quote("HDFCBANK")
            print(f"✅ Data provider integration working!")
            print(f"   Fetched: {quote.symbol} = ₹{quote.price}")
        
        return True
    except Exception as e:
        print(f"❌ Data provider integration test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

try:
    result = asyncio.run(test_data_provider())
except Exception as e:
    print(f"❌ Async test failed: {e}")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

if INDIANAPI_KEY:
    print("✅ API Key: Configured (Premium tier)")
else:
    print("ℹ️ API Key: Not configured (FREE tier)")

print("\nAPI Key Status:")
print(f"  - Loaded from config: {'Yes' if INDIANAPI_KEY else 'No'}")
print(f"  - Provider initialized: Yes")
print(f"  - Ready to use: Yes")

print("\nNext Steps:")
if INDIANAPI_KEY:
    print("  1. ✅ API key is configured")
    print("  2. ✅ Provider is initialized")
    print("  3. Test with real stock symbols:")
    print("     - RELIANCE, TCS, INFY, HDFCBANK, etc.")
    print("  4. Monitor logs for 'Premium tier' message")
else:
    print("  1. ℹ️ Using FREE tier (no API key)")
    print("  2. ✅ Provider is initialized")
    print("  3. FREE tier works for basic endpoints")
    print("  4. Add INDIANAPI_KEY to .env for premium features")

print("\nAPI Endpoint Tests:")
print("  - Stock Quote: Check logs above")
print("  - Historical Data: Check logs above")
print("  - Company Profile: Check logs above")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)

print("\nTo test with the full app:")
print("  1. Start backend: python QuantPulse-Backend/run.py")
print("  2. Test endpoint: curl http://localhost:8000/api/v2/analyze/RELIANCE")
print("  3. Check logs for IndianAPI usage")
