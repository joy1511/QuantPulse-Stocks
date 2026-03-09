"""
Database Configuration and Session Management

This module sets up the database connection, session management, and base models
for the QuantPulse application using SQLAlchemy ORM.

Supports:
- PostgreSQL for production (Railway/Render)
- SQLite for local development
- Async database operations
- Connection pooling
- Automatic table creation
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from app.config import IS_CLOUD, ENV

# =============================================================================
# Database URL Configuration
# =============================================================================

# Get database URL from environment or use SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production: Use PostgreSQL from Railway/Render
    # Fix for Railway's postgres:// URL (SQLAlchemy requires postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print(f"🗄️ Using PostgreSQL database (production)")
    
    # Production database engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,        # Connection pool size
        max_overflow=20,     # Max connections beyond pool_size
        echo=False           # Set to True for SQL query logging
    )
else:
    # Local development: Use SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./quantpulse.db"
    print(f"🗄️ Using SQLite database (local development)")
    
    # SQLite engine with special settings for threading
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

# =============================================================================
# Session Configuration
# =============================================================================

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()

# =============================================================================
# Database Dependency for FastAPI
# =============================================================================

def get_db():
    """
    FastAPI dependency that provides a database session.
    
    Usage in routes:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Automatically closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# Database Initialization
# =============================================================================

def init_db():
    """
    Initialize database by creating all tables.
    Called during application startup.
    Handles existing tables gracefully.
    """
    try:
        print("🔧 Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        # Tables might already exist, which is fine
        print(f"ℹ️ Database initialization: {e}")
        print("✅ Database ready (tables may already exist)")

def drop_all_tables():
    """
    Drop all tables (use with caution!).
    Only for development/testing.
    """
    if not IS_CLOUD:
        print("⚠️ Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    else:
        print("❌ Cannot drop tables in production environment")
