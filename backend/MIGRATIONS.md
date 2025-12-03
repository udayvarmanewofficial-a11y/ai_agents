# Database Migrations

## Overview

The application includes an automatic migration system that ensures the database schema is always up to date. Migrations run automatically on application startup.

## How It Works

1. On startup, the application runs `init_db()` to create base tables
2. Then it runs `run_migrations()` to apply any schema updates
3. Each migration uses `IF NOT EXISTS` or similar safe SQL to prevent errors on re-runs

## Adding New Migrations

To add a new database migration, edit `/backend/app/db/migrations.py`:

```python
migrations = [
    {
        "name": "add_use_custom_rag_column",
        "description": "Add use_custom_rag column to tasks table",
        "sql": """
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS use_custom_rag INTEGER DEFAULT 0 NOT NULL;
        """
    },
    {
        "name": "your_new_migration",
        "description": "What this migration does",
        "sql": """
            ALTER TABLE your_table
            ADD COLUMN IF NOT EXISTS your_column VARCHAR(255);
        """
    },
]
```

## Best Practices

1. **Use IF NOT EXISTS**: Always use `IF NOT EXISTS` or equivalent to make migrations idempotent
2. **Add to the end**: Append new migrations to the list, don't modify existing ones
3. **Test locally**: Test migrations on your local database before deploying
4. **Use safe operations**: Prefer `ADD COLUMN` over `DROP COLUMN`, consider data migration needs

## Manual Migration Run

You can also run migrations manually:

```bash
cd backend
source venv/bin/activate
python -m app.db.migrations
```

## Current Migrations

- `add_use_custom_rag_column`: Adds the `use_custom_rag` column to the tasks table for RAG control
