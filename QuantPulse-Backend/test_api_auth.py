"""
Test different API key authentication methods
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

INDIANAPI_KEY = os.getenv("INDIANAPI_KEY")
masked_key = f"{INDIANAPI_KEY[:8]}...{INDIANAPI_KEY[-4:]}" if INDIANAPI_KEY else "None"

print("=" * 60)
print("Testing API Key Authentication Methods")
print("=" * 60)
print(f"\nAPI Key: {masked_key}")

async def test_auth_methods():
    """Try different authentication methods"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Method 1: apikey header (lowercase)
        print("\n" + "=" * 60)
        print("Method 1: 'apikey' header (lowercase)")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"apikey": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 2: API-Key header
        print("\n" + "=" * 60)
        print("Method 2: 'API-Key' header")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"API-Key": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 3: X-API-Key header
        print("\n" + "=" * 60)
        print("Method 3: 'X-API-Key' header")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"X-API-Key": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 4: Authorization Bearer
        print("\n" + "=" * 60)
        print("Method 4: 'Authorization: Bearer' header")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"Authorization": f"Bearer {INDIANAPI_KEY}"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 5: Query parameter
        print("\n" + "=" * 60)
        print("Method 5: Query parameter 'apikey'")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                params={"apikey": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 6: Query parameter 'api_key'
        print("\n" + "=" * 60)
        print("Method 6: Query parameter 'api_key'")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                params={"api_key": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 7: APIKEY header (uppercase)
        print("\n" + "=" * 60)
        print("Method 7: 'APIKEY' header (uppercase)")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"APIKEY": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 8: x-api-key (lowercase with dashes)
        print("\n" + "=" * 60)
        print("Method 8: 'x-api-key' header (lowercase)")
        print("=" * 60)
        
        try:
            response = await client.get(
                "https://stock.indianapi.in/trending",
                headers={"x-api-key": INDIANAPI_KEY}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_auth_methods())

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nLook for Status: 200 to find the correct method")
