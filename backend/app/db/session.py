"""
Database connection and session management.
"""

from typing import Generator

from app.core.config import settings
from app.core.logging import app_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

# Create database engine
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models.database import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables created successfully")
    except Exception as e:
        app_logger.error(f"Failed to create database tables: {e}")
        raise
