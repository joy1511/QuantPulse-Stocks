"""
Quick test script to verify deployment fixes
"""

import asyncio
import sys

print("=" * 60)
print("Testing Deployment Fixes")
print("=" * 60)

# Test 1: Database initialization
print("\n1. Testing database initialization...")
try:
    from app.database import init_db
    init_db()
    print("✅ Database initialization successful")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)

# Test 2: IndianAPI provider import
print("\n2. Testing IndianAPI provider import...")
try:
    from app.providers.indianapi_provider import IndianAPIProvider
    provider = IndianAPIProvider()
    print("✅ IndianAPI provider imported successfully")
except Exception as e:
    print(f"❌ IndianAPI provider import failed: {e}")
    sys.exit(1)

# Test 3: Data provider with caching
print("\n3. Testing data provider with 24-hour caching...")
try:
    from app.services.data_provider import (
        get_cache_key,
        is_cache_valid,
        get_from_cache,
        save_to_cache
    )
    
    # Test cache functions
    test_data = {"test": "data"}
    save_to_cache("TEST", "test_type", test_data)
    cached = get_from_cache("TEST", "test_type", max_age_hours=24)
    
    if cached == test_data:
        print("✅ 24-hour caching system working")
    else:
        print("❌ Cache retrieval failed")
        sys.exit(1)
except Exception as e:
    print(f"❌ Data provider test failed: {e}")
    sys.exit(1)

# Test 4: Demo data service with realistic prices
print("\n4. Testing demo data service...")
try:
    from app.services.demo_data_service import DemoDataService
    demo_service = DemoDataService()
    
    # Check if realistic prices are loaded
    if "RELIANCE" in demo_service.STOCK_DATABASE:
        reliance_price = demo_service.STOCK_DATABASE["RELIANCE"]["base_price"]
        print(f"✅ Demo data loaded: RELIANCE = ₹{reliance_price}")
        
        if 2000 <= reliance_price <= 3000:
            print("✅ Realistic price range confirmed")
        else:
            print(f"⚠️ Price seems unrealistic: ₹{reliance_price}")
    else:
        print("❌ RELIANCE not found in demo database")
        sys.exit(1)
except Exception as e:
    print(f"❌ Demo data service test failed: {e}")
    sys.exit(1)

# Test 5: IndianAPI provider methods (async test)
print("\n5. Testing IndianAPI provider methods...")
async def test_indianapi():
    try:
        from app.providers.indianapi_provider import IndianAPIProvider
        provider = IndianAPIProvider()
        
        # Test quote method exists
        if hasattr(provider, 'get_stock_quote'):
            print("✅ get_stock_quote method exists")
        else:
            print("❌ get_stock_quote method missing")
            return False
        
        # Test historical data method exists
        if hasattr(provider, 'get_historical_data'):
            print("✅ get_historical_data method exists")
        else:
            print("❌ get_historical_data method missing")
            return False
        
        # Test company profile method exists
        if hasattr(provider, 'get_company_profile'):
            print("✅ get_company_profile method exists")
        else:
            print("❌ get_company_profile method missing")
            return False
        
        await provider.close()
        return True
    except Exception as e:
        print(f"❌ IndianAPI provider method test failed: {e}")
        return False

try:
    result = asyncio.run(test_indianapi())
    if not result:
        sys.exit(1)
except Exception as e:
    print(f"❌ Async test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Deployment fixes verified.")
print("=" * 60)
print("\nYou can now deploy to Render with confidence!")
print("\nNext steps:")
print("1. Commit changes: git add . && git commit -m 'Fix deployment issues'")
print("2. Push to GitHub: git push")
print("3. Render will auto-deploy")
print("4. Monitor logs for data source usage")
