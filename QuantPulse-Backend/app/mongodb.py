"""
MongoDB Database Connection

This file handles the connection to MongoDB database.
It reads the connection URL from the .env file and provides
a simple interface to access the database.
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

# MongoDB client instance (will be initialized on startup)
mongodb_client: AsyncIOMotorClient = None
mongodb_database = None


def get_mongodb_url() -> str:
    """
    Get MongoDB connection URL from environment variables.
    
    Returns:
        str: MongoDB connection URL
    """
    # Try to get from environment variable
    mongodb_url = os.getenv("MONGODB_URL")
    
    if not mongodb_url:
        logger.warning("⚠️ MONGODB_URL not found in environment variables")
        return None
    
    return mongodb_url


async def connect_to_mongodb():
    """
    Connect to MongoDB database.
    This function is called when the application starts.
    """
    global mongodb_client, mongodb_database
    
    mongodb_url = get_mongodb_url()
    
    if not mongodb_url:
        logger.error("❌ Cannot connect to MongoDB: MONGODB_URL not configured")
        return False
    
    try:
        # Create MongoDB client
        logger.info("🔌 Connecting to MongoDB...")
        mongodb_client = AsyncIOMotorClient(mongodb_url)
        
        # Test the connection
        await mongodb_client.admin.command('ping')
        
        # Get database name from URL or use default
        # Extract database name from connection string
        if "/" in mongodb_url:
            db_name = mongodb_url.split("/")[-1].split("?")[0]
            if db_name:
                mongodb_database = mongodb_client[db_name]
            else:
                mongodb_database = mongodb_client["quantpulse"]
        else:
            mongodb_database = mongodb_client["quantpulse"]
        
        logger.info(f"✅ Connected to MongoDB successfully!")
        logger.info(f"📊 Database: {mongodb_database.name}")
        return True
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
        return False


async def close_mongodb_connection():
    """
    Close MongoDB connection.
    This function is called when the application shuts down.
    """
    global mongodb_client
    
    if mongodb_client:
        logger.info("🔌 Closing MongoDB connection...")
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed")


def get_database():
    """
    Get the MongoDB database instance.
    
    Returns:
        Database: MongoDB database instance
        
    Example:
        db = get_database()
        users_collection = db["users"]
        user = await users_collection.find_one({"email": "test@example.com"})
    """
    if mongodb_database is None:
        logger.error("❌ MongoDB database not initialized. Call connect_to_mongodb() first.")
        return None
    
    return mongodb_database


def get_collection(collection_name: str):
    """
    Get a MongoDB collection by name.
    
    Args:
        collection_name: Name of the collection (e.g., "users", "stocks", "predictions")
        
    Returns:
        Collection: MongoDB collection instance
        
    Example:
        users = get_collection("users")
        user = await users.find_one({"email": "test@example.com"})
    """
    db = get_database()
    if db is None:
        return None
    
    return db[collection_name]


# Health check function
async def check_mongodb_health() -> dict:
    """
    Check if MongoDB connection is healthy.
    
    Returns:
        dict: Health status information
    """
    if mongodb_client is None:
        return {
            "status": "disconnected",
            "message": "MongoDB client not initialized"
        }
    
    try:
        # Ping the database
        await mongodb_client.admin.command('ping')
        
        return {
            "status": "connected",
            "database": mongodb_database.name if mongodb_database else "unknown",
            "message": "MongoDB connection is healthy"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB connection error: {str(e)}"
        }
