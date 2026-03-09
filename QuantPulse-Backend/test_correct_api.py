"""
Test Indian Stock API with Correct Base URL

Base URL: https://stock.indianapi.in
API Key: From .env file
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

INDIANAPI_KEY = os.getenv("INDIANAPI_KEY")

print("=" * 60)
print("Testing Indian Stock API (Correct Base URL)")
print("=" * 60)

if INDIANAPI_KEY:
    masked_key = f"{INDIANAPI_KEY[:8]}...{INDIANAPI_KEY[-4:]}"
    print(f"\n✅ API Key loaded: {masked_key}")
else:
    print("\n⚠️ No API key found")

async def test_api():
    """Test the correct API endpoints"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: IPO Data (from screenshot)
        print("\n" + "=" * 60)
        print("Test 1: IPO Data Endpoint")
        print("=" * 60)
        
        try:
            url = "https://stock.indianapi.in/ipo"
            headers = {"apikey": INDIANAPI_KEY} if INDIANAPI_KEY else {}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Headers: apikey={masked_key if INDIANAPI_KEY else 'None'}")
            
            response = await client.get(url, headers=headers)
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got JSON data")
                print(f"  Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"  Items: {len(data)}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 2: Stock Details (from screenshot)
        print("\n" + "=" * 60)
        print("Test 2: Stock Details Endpoint")
        print("=" * 60)
        
        try:
            url = "https://stock.indianapi.in/stock"
            params = {"symbol": "RELIANCE"}  # Try with symbol parameter
            headers = {"apikey": INDIANAPI_KEY} if INDIANAPI_KEY else {}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Params: {params}")
            print(f"  Headers: apikey={masked_key if INDIANAPI_KEY else 'None'}")
            
            response = await client.get(url, params=params, headers=headers)
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got JSON data")
                print(f"  Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:10]}")
                    # Try to extract price
                    if 'price' in data:
                        print(f"  Price: ₹{data['price']}")
                    if 'currentPrice' in data:
                        print(f"  Current Price: ₹{data['currentPrice']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 3: Trending Stocks (from screenshot)
        print("\n" + "=" * 60)
        print("Test 3: Trending Stocks Endpoint")
        print("=" * 60)
        
        try:
            url = "https://stock.indianapi.in/trending"
            headers = {"apikey": INDIANAPI_KEY} if INDIANAPI_KEY else {}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Headers: apikey={masked_key if INDIANAPI_KEY else 'None'}")
            
            response = await client.get(url, headers=headers)
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got JSON data")
                print(f"  Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:5]}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 4: News Data (from screenshot)
        print("\n" + "=" * 60)
        print("Test 4: News Data Endpoint")
        print("=" * 60)
        
        try:
            url = "https://stock.indianapi.in/news"
            headers = {"apikey": INDIANAPI_KEY} if INDIANAPI_KEY else {}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Headers: apikey={masked_key if INDIANAPI_KEY else 'None'}")
            
            response = await client.get(url, headers=headers)
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got JSON data")
                print(f"  Type: {type(data)}")
                if isinstance(data, list):
                    print(f"  News items: {len(data)}")
                    if data:
                        print(f"  First item keys: {list(data[0].keys())[:5]}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 5: Commodities (from screenshot)
        print("\n" + "=" * 60)
        print("Test 5: Commodities Endpoint")
        print("=" * 60)
        
        try:
            url = "https://stock.indianapi.in/commodities"
            headers = {"apikey": INDIANAPI_KEY} if INDIANAPI_KEY else {}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Headers: apikey={masked_key if INDIANAPI_KEY else 'None'}")
            
            response = await client.get(url, headers=headers)
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got JSON data")
                print(f"  Type: {type(data)}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

print("\nRunning tests...")
asyncio.run(test_api())

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)

print("\nNote: The API key should be passed as 'apikey' header")
print("Base URL: https://stock.indianapi.in")
