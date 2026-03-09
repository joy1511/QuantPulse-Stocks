"""Simple test without emojis for Windows"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from app.providers.indianapi_provider import IndianAPIProvider
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("INDIANAPI_KEY")
    
    print("Testing IndianAPI with correct settings...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    
    provider = IndianAPIProvider(api_key=api_key)
    
    # Test 1: Stock quote
    print("\n1. Testing stock quote for RELIANCE...")
    try:
        quote = await provider.get_stock_quote("RELIANCE")
        print(f"SUCCESS! Price: Rs.{quote.price}")
        print(f"  Change: Rs.{quote.change} ({quote.percent_change}%)")
        print(f"  Volume: {quote.volume:,}")
        print(f"  Exchange: {quote.exchange}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    # Test 2: Historical data
    print("\n2. Testing historical data for TCS...")
    try:
        hist = await provider.get_historical_data("TCS", period="1y")
        print(f"SUCCESS! Got {len(hist.data)} data points")
        if hist.data:
            print(f"  First: {hist.data[0]['date']} - Rs.{hist.data[0]['close']}")
            print(f"  Last: {hist.data[-1]['date']} - Rs.{hist.data[-1]['close']}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    # Test 3: Company profile
    print("\n3. Testing company profile for INFY...")
    try:
        profile = await provider.get_company_profile("INFY")
        print(f"SUCCESS! {profile.name}")
        print(f"  Sector: {profile.sector}")
        print(f"  Industry: {profile.industry}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    await provider.close()
    print("\nAll tests complete!")

asyncio.run(test())
