"""
Update user verification status in MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def update_user_verified(email: str):
    """Update user to set is_verified=True"""
    
    # Get MongoDB connection string
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("❌ MONGODB_URL not found in .env file")
        return
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client.quantpulse
    users_collection = db.users
    
    try:
        # Update user
        result = await users_collection.update_one(
            {"email": email},
            {"$set": {"is_verified": True, "is_active": True}}
        )
        
        if result.matched_count == 0:
            print(f"❌ User not found: {email}")
        elif result.modified_count > 0:
            print(f"✅ User updated successfully: {email}")
            print(f"   - is_verified: True")
            print(f"   - is_active: True")
        else:
            print(f"ℹ️  User already verified: {email}")
        
        # Show user details
        user = await users_collection.find_one({"email": email})
        if user:
            print(f"\n📋 User Details:")
            print(f"   - Email: {user['email']}")
            print(f"   - Name: {user.get('full_name', 'N/A')}")
            print(f"   - Active: {user.get('is_active', False)}")
            print(f"   - Verified: {user.get('is_verified', False)}")
            print(f"   - User ID: {user['_id']}")
    
    finally:
        client.close()

if __name__ == "__main__":
    email = "riddhisharma140606@gmail.com"
    asyncio.run(update_user_verified(email))
