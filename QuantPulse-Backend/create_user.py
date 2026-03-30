"""
Create User Script

Creates a user account in MongoDB database.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.mongodb import connect_to_mongodb, close_mongodb_connection, get_collection
from app.services.auth_service import get_password_hash
from datetime import datetime


async def create_user(email: str, full_name: str, password: str):
    """Create a new user account"""
    
    print("\n" + "="*60)
    print("👤 Creating User Account")
    print("="*60 + "\n")
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB...")
    connection_success = await connect_to_mongodb()
    
    if not connection_success:
        print("❌ Failed to connect to MongoDB")
        return False
    
    print("✅ Connected to MongoDB")
    print()
    
    # Get users collection
    users_collection = get_collection("users")
    if users_collection is None:
        print("❌ Failed to get users collection")
        return False
    
    # Check if user already exists
    print(f"🔍 Checking if user exists: {email}")
    existing_user = await users_collection.find_one({"email": email})
    
    if existing_user:
        print(f"⚠️  User already exists with email: {email}")
        print(f"   User ID: {existing_user['_id']}")
        print(f"   Name: {existing_user.get('full_name', 'N/A')}")
        print(f"   Created: {existing_user.get('created_at', 'N/A')}")
        return False
    
    print("✅ Email is available")
    print()
    
    # Create user document
    print("📝 Creating user account...")
    user_doc = {
        "email": email,
        "hashed_password": get_password_hash(password),
        "full_name": full_name,
        "is_active": True,
        "is_verified": True,  # Auto-verify for manual creation
        "is_admin": False,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Insert into MongoDB
    result = await users_collection.insert_one(user_doc)
    
    print("="*60)
    print("🎉 SUCCESS! User account created!")
    print("="*60)
    print()
    print(f"📧 Email: {email}")
    print(f"👤 Name: {full_name}")
    print(f"🆔 User ID: {result.inserted_id}")
    print(f"✅ Status: Active & Verified")
    print(f"📅 Created: {user_doc['created_at']}")
    print()
    print("✅ You can now login with these credentials!")
    print()
    
    # Close connection
    await close_mongodb_connection()
    
    return True


async def main():
    """Main function"""
    
    # User details
    email = "riddhisharma140606@gmail.com"
    full_name = "Riddhi Sharma"
    password = "R23314@riddhi"
    
    success = await create_user(email, full_name, password)
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
