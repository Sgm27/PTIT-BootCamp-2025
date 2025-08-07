"""
Enhanced Database Configuration with SQLAlchemy ORM
Supports PostgreSQL with connection pooling and environment variables
"""
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import psycopg2
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '13.216.164.63'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'healthcare_ai'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}

# SQLAlchemy Configuration
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=os.getenv('DB_DEBUG', 'false').lower() == 'true'
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_connection():
    """Get raw psycopg2 connection for legacy code"""
    return psycopg2.connect(**DB_CONFIG)

@contextmanager
def get_db() -> Session:
    """
    Context manager for database sessions
    Ensures proper session cleanup
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """Get database session for dependency injection"""
    return SessionLocal()

def init_database():
    """Initialize database and create all tables"""
    try:
        # Import all models to ensure they're registered
        import db.models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False 