"""
Test Market Movers endpoint and verify data structure
"""
import asyncio
import httpx
from datetime import datetime

async def test_market_movers():
    print(f"\n{'='*60}")
    print(f"Testing Market Movers Endpoint")
    print(f"{'='*60}")
    print(f"Time: {datetime.now()}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test backend endpoint
            response = await client.get("http://localhost:8000/api/market/trending")
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Endpoint Status: {response.status_code}")
            print(f"✅ Top Gainers: {len(data.get('top_gainers', []))} stocks")
            print(f"✅ Top Losers: {len(data.get('top_losers', []))} stocks")
            print(f"✅ Cached: {data.get('cached', False)}")
            print(f"✅ Timestamp: {data.get('timestamp', 'N/A')}")
            
            # Show sample data
            if data.get('top_gainers'):
                print(f"\n📈 Sample Gainer:")
                gainer = data['top_gainers'][0]
                print(f"   Company: {gainer.get('company', 'N/A')}")
                print(f"   Ticker: {gainer.get('ticker', 'N/A')}")
                print(f"   Price: ₹{gainer.get('price', 0)}")
                print(f"   Change: +{gainer.get('percent_change', 0)}%")
            
            if data.get('top_losers'):
                print(f"\n📉 Sample Loser:")
                loser = data['top_losers'][0]
                print(f"   Company: {loser.get('company', 'N/A')}")
                print(f"   Ticker: {loser.get('ticker', 'N/A')}")
                print(f"   Price: ₹{loser.get('price', 0)}")
                print(f"   Change: {loser.get('percent_change', 0)}%")
            
            # Test CORS headers
            print(f"\n🔒 CORS Headers:")
            print(f"   Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin', 'Not set')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_market_movers())
    print(f"\n{'='*60}")
    print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"{'='*60}\n")
