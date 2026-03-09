"""
Debug IndianAPI.in API Responses

This script helps debug what the API is actually returning.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

INDIANAPI_KEY = os.getenv("INDIANAPI_KEY")

print("=" * 60)
print("Debugging IndianAPI.in API Responses")
print("=" * 60)

if INDIANAPI_KEY:
    masked_key = f"{INDIANAPI_KEY[:8]}...{INDIANAPI_KEY[-4:]}"
    print(f"\n✅ API Key loaded: {masked_key}")
    print(f"   Length: {len(INDIANAPI_KEY)} characters")
else:
    print("\nℹ️ No API key - testing FREE tier")

async def test_api_call():
    """Test raw API call to see actual response"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Basic call without API key
        print("\n" + "=" * 60)
        print("Test 1: Basic API call (no auth)")
        print("=" * 60)
        
        try:
            url = "https://indianapi.in/stock"
            params = {"name": "RELIANCE"}
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  Params: {params}")
            print(f"  Headers: Basic (no auth)")
            
            response = await client.get(url, params=params)
            
            print(f"\nResponse:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Content Length: {len(response.content)} bytes")
            
            # Try to decode as text first
            print(f"\nRaw Content (first 500 chars):")
            print(response.text[:500])
            
            # Try to parse as JSON
            if response.text:
                try:
                    data = response.json()
                    print(f"\n✅ JSON parsed successfully!")
                    print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except Exception as e:
                    print(f"\n❌ JSON parsing failed: {e}")
            else:
                print(f"\n⚠️ Empty response body")
                
        except Exception as e:
            print(f"\n❌ Request failed: {e}")
        
        # Test 2: With API key in Authorization header
        if INDIANAPI_KEY:
            print("\n" + "=" * 60)
            print("Test 2: API call with Authorization header")
            print("=" * 60)
            
            try:
                url = "https://indianapi.in/stock"
                params = {"name": "RELIANCE"}
                headers = {
                    "Authorization": f"Bearer {INDIANAPI_KEY}",
                    "Content-Type": "application/json"
                }
                
                print(f"\nRequest:")
                print(f"  URL: {url}")
                print(f"  Params: {params}")
                print(f"  Headers: Authorization: Bearer {masked_key}")
                
                response = await client.get(url, params=params, headers=headers)
                
                print(f"\nResponse:")
                print(f"  Status Code: {response.status_code}")
                print(f"  Content-Type: {response.headers.get('content-type')}")
                print(f"  Content Length: {len(response.content)} bytes")
                
                print(f"\nRaw Content (first 500 chars):")
                print(response.text[:500])
                
                if response.text:
                    try:
                        data = response.json()
                        print(f"\n✅ JSON parsed successfully!")
                        print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except Exception as e:
                        print(f"\n❌ JSON parsing failed: {e}")
                else:
                    print(f"\n⚠️ Empty response body")
                    
            except Exception as e:
                print(f"\n❌ Request failed: {e}")
        
        # Test 3: With API key in X-API-Key header
        if INDIANAPI_KEY:
            print("\n" + "=" * 60)
            print("Test 3: API call with X-API-Key header")
            print("=" * 60)
            
            try:
                url = "https://indianapi.in/stock"
                params = {"name": "RELIANCE"}
                headers = {
                    "X-API-Key": INDIANAPI_KEY,
                    "Content-Type": "application/json"
                }
                
                print(f"\nRequest:")
                print(f"  URL: {url}")
                print(f"  Params: {params}")
                print(f"  Headers: X-API-Key: {masked_key}")
                
                response = await client.get(url, params=params, headers=headers)
                
                print(f"\nResponse:")
                print(f"  Status Code: {response.status_code}")
                print(f"  Content-Type: {response.headers.get('content-type')}")
                print(f"  Content Length: {len(response.content)} bytes")
                
                print(f"\nRaw Content (first 500 chars):")
                print(response.text[:500])
                
                if response.text:
                    try:
                        data = response.json()
                        print(f"\n✅ JSON parsed successfully!")
                        print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except Exception as e:
                        print(f"\n❌ JSON parsing failed: {e}")
                else:
                    print(f"\n⚠️ Empty response body")
                    
            except Exception as e:
                print(f"\n❌ Request failed: {e}")
        
        # Test 4: Try trending endpoint (no params needed)
        print("\n" + "=" * 60)
        print("Test 4: Trending endpoint (simpler test)")
        print("=" * 60)
        
        try:
            url = "https://indianapi.in/trending"
            
            print(f"\nRequest:")
            print(f"  URL: {url}")
            print(f"  No params")
            
            response = await client.get(url)
            
            print(f"\nResponse:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Content Length: {len(response.content)} bytes")
            
            print(f"\nRaw Content (first 500 chars):")
            print(response.text[:500])
            
            if response.text:
                try:
                    data = response.json()
                    print(f"\n✅ JSON parsed successfully!")
                    print(f"   Type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                except Exception as e:
                    print(f"\n❌ JSON parsing failed: {e}")
            else:
                print(f"\n⚠️ Empty response body")
                
        except Exception as e:
            print(f"\n❌ Request failed: {e}")

print("\nRunning API tests...")
asyncio.run(test_api_call())

print("\n" + "=" * 60)
print("Debug Complete!")
print("=" * 60)

print("\nConclusions:")
print("  1. Check which test returned valid JSON")
print("  2. Check if API key authentication is working")
print("  3. Check if the API endpoints are correct")
print("  4. Check IndianAPI.in documentation for auth method")
