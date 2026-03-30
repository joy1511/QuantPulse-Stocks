"""
Test script to check live price accuracy from different sources
"""
import asyncio
import httpx
from datetime import datetime

INDIANAPI_KEY = "your_key_here"  # Will be loaded from env

async def test_indianapi_price(symbol: str):
    """Test IndianAPI /stock endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing IndianAPI for {symbol}")
    print(f"{'='*60}")
    
    headers = {"Content-Type": "application/json", "User-Agent": "QuantPulse/2.0"}
    if INDIANAPI_KEY:
        headers["X-API-Key"] = INDIANAPI_KEY
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://stock.indianapi.in/stock",
                params={"name": symbol},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            current_price_data = data.get("currentPrice", {})
            nse_price = current_price_data.get("NSE")
            bse_price = current_price_data.get("BSE")
            percent_change = data.get("percentChange", 0.0)
            
            print(f"NSE Price: ₹{nse_price}")
            print(f"BSE Price: ₹{bse_price}")
            print(f"Percent Change: {percent_change}%")
            print(f"Timestamp: {datetime.now()}")
            
            return nse_price or bse_price
            
        except Exception as e:
            print(f"❌ IndianAPI failed: {e}")
            return None

async def test_yfinance_price(symbol: str):
    """Test yfinance for comparison"""
    print(f"\n{'='*60}")
    print(f"Testing yfinance for {symbol}")
    print(f"{'='*60}")
    
    try:
        import yfinance as yf
        
        yf_symbol = f"{symbol}.NS"
        ticker = yf.Ticker(yf_symbol)
        
        # Get latest data
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            latest_close = float(hist['Close'].iloc[-1])
            latest_date = hist.index[-1]
            print(f"Latest Close: ₹{latest_close}")
            print(f"Date: {latest_date}")
            print(f"Timestamp: {datetime.now()}")
            return latest_close
        else:
            print("❌ No data from yfinance")
            return None
            
    except Exception as e:
        print(f"❌ yfinance failed: {e}")
        return None

async def test_backend_endpoint(symbol: str):
    """Test our backend endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing Backend /stock/{symbol}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"http://localhost:8000/stock/{symbol}")
            response.raise_for_status()
            data = response.json()
            
            print(f"Current Price: ₹{data['currentPrice']}")
            print(f"Previous Close: ₹{data['previousClose']}")
            print(f"Change: ₹{data['change']} ({data['changePercent']}%)")
            print(f"Is Demo: {data.get('isDemoData', False)}")
            print(f"Provider: {data.get('service_info', {}).get('provider_status', {}).get('primary_provider', 'Unknown')}")
            print(f"Cached: {data.get('service_info', {}).get('cached', False)}")
            
            return data['currentPrice']
            
        except Exception as e:
            print(f"❌ Backend failed: {e}")
            return None

async def main():
    # Load API key from env
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    global INDIANAPI_KEY
    INDIANAPI_KEY = os.getenv("INDIANAPI_KEY", "")
    
    symbol = "TCS"
    
    print(f"\n🔍 LIVE PRICE ACCURACY TEST")
    print(f"Symbol: {symbol}")
    print(f"Time: {datetime.now()}")
    print(f"Expected: ₹2,365 (user reported)")
    
    # Test all sources
    indianapi_price = await test_indianapi_price(symbol)
    yfinance_price = await test_yfinance_price(symbol)
    backend_price = await test_backend_endpoint(symbol)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Expected Price:  ₹2,365.00")
    print(f"IndianAPI:       ₹{indianapi_price if indianapi_price else 'N/A'}")
    print(f"yfinance:        ₹{yfinance_price if yfinance_price else 'N/A'}")
    print(f"Backend:         ₹{backend_price if backend_price else 'N/A'}")
    
    # Check which is closest
    expected = 2365.0
    if indianapi_price:
        diff_indian = abs(float(indianapi_price) - expected)
        print(f"\nIndianAPI diff: ₹{diff_indian:.2f}")
    if yfinance_price:
        diff_yf = abs(float(yfinance_price) - expected)
        print(f"yfinance diff:  ₹{diff_yf:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
