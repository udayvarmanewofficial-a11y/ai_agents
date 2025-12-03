"""
Database migration utilities to ensure schema is up to date.
Run this on startup to apply any missing schema changes.
"""

from app.core.logging import app_logger
from app.db.session import engine
from sqlalchemy import text


def run_migrations():
    """
    Apply all database migrations to ensure schema is up to date.
    This is safe to run on every startup - it only applies missing changes.
    """
    migrations = [
        {
            "name": "add_use_custom_rag_column",
            "description": "Add use_custom_rag column to tasks table",
            "sql": """
                ALTER TABLE tasks 
                ADD COLUMN IF NOT EXISTS use_custom_rag INTEGER DEFAULT 0 NOT NULL;
            """
        },
        # Add more migrations here as needed
        # {
        #     "name": "add_new_column",
        #     "description": "Description of the migration",
        #     "sql": "ALTER TABLE ... ADD COLUMN IF NOT EXISTS ..."
        # },
    ]
    
    app_logger.info("Running database migrations...")
    
    with engine.connect() as conn:
        for migration in migrations:
            try:
                app_logger.info(f"Applying migration: {migration['name']}")
                conn.execute(text(migration['sql']))
                conn.commit()
                app_logger.info(f"✓ Migration '{migration['name']}' applied successfully")
            except Exception as e:
                app_logger.error(f"✗ Migration '{migration['name']}' failed: {e}")
                # Continue with other migrations even if one fails
                conn.rollback()
    
    app_logger.info("Database migrations completed")


if __name__ == "__main__":
    # Allow running migrations directly
    run_migrations()
