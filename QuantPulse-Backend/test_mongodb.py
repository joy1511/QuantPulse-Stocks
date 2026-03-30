"""
MongoDB Connection Test Script

This script tests if your MongoDB connection is working correctly.
It will:
1. Try to connect to MongoDB using the URL from .env file
2. Test basic operations (insert, read, delete)
3. Show you if everything is working

Run this script with: python test_mongodb.py
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import MongoDB functions
from app.mongodb import connect_to_mongodb, close_mongodb_connection, get_collection, check_mongodb_health


async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    
    print("\n" + "="*60)
    print("🧪 MongoDB Connection Test")
    print("="*60 + "\n")
    
    # Step 1: Check if MONGODB_URL is set
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL not found in .env file")
        print("\n📝 Please add MONGODB_URL to your .env file")
        print("   Example: MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/quantpulse")
        return False
    
    print(f"✅ Found MONGODB_URL in .env file")
    print(f"   URL: {mongodb_url[:20]}...{mongodb_url[-20:] if len(mongodb_url) > 40 else ''}")
    print()
    
    # Step 2: Try to connect
    print("🔌 Attempting to connect to MongoDB...")
    connection_success = await connect_to_mongodb()
    
    if not connection_success:
        print("❌ Failed to connect to MongoDB")
        print("\n🔍 Common issues:")
        print("   1. Check if your MongoDB URL is correct")
        print("   2. Check if your IP address is whitelisted in MongoDB Atlas")
        print("   3. Check if your username/password is correct")
        print("   4. Check your internet connection")
        return False
    
    print("✅ Successfully connected to MongoDB!")
    print()
    
    # Step 3: Check health
    print("🏥 Checking MongoDB health...")
    health = await check_mongodb_health()
    print(f"   Status: {health['status']}")
    print(f"   Database: {health.get('database', 'N/A')}")
    print(f"   Message: {health['message']}")
    print()
    
    # Step 4: Test basic operations
    print("📝 Testing basic database operations...")
    
    try:
        # Get a test collection
        test_collection = get_collection("test_collection")
        
        if test_collection is None:
            print("❌ Failed to get collection")
            return False
        
        # Insert a test document
        print("   → Inserting test document...")
        test_doc = {
            "test": "Hello MongoDB!",
            "timestamp": "2024-01-01",
            "status": "testing"
        }
        result = await test_collection.insert_one(test_doc)
        print(f"   ✅ Inserted document with ID: {result.inserted_id}")
        
        # Read the document back
        print("   → Reading document back...")
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print(f"   ✅ Found document: {found_doc['test']}")
        else:
            print("   ❌ Could not find document")
            return False
        
        # Delete the test document
        print("   → Cleaning up test document...")
        delete_result = await test_collection.delete_one({"_id": result.inserted_id})
        print(f"   ✅ Deleted {delete_result.deleted_count} document(s)")
        
        print()
        print("="*60)
        print("🎉 SUCCESS! MongoDB is working perfectly!")
        print("="*60)
        print()
        print("✅ Your MongoDB connection is ready to use")
        print("✅ You can now run your application with: python run.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during operations: {e}")
        return False
    
    finally:
        # Close connection
        await close_mongodb_connection()


async def main():
    """Main function"""
    success = await test_mongodb_connection()
    
    if not success:
        print("\n❌ MongoDB test failed")
        print("\n📚 Need help? Check the instructions in the output above")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
