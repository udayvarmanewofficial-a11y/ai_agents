#!/usr/bin/env python3
"""
Initialize database schema using SQLAlchemy create_all().
This bypasses Alembic and creates tables directly.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.db.session import engine
from app.models.database import Base


def init_database():
    """Create all database tables."""
    print("🗄️  Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
