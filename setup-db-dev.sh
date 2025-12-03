#!/bin/bash

set -e

echo "🗄️  Setting up database..."

# Check if PostgreSQL is running
if ! docker ps | grep -q planner-postgres-dev; then
    echo "❌ PostgreSQL container is not running!"
    echo "Start it with: docker-compose -f docker-compose.dev.yml up -d postgres"
    exit 1
fi

echo "Waiting for PostgreSQL to be ready..."
sleep 3

cd backend
source venv/bin/activate

# Generate initial migration if none exists
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "Generating initial database migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "✅ Database setup complete!"
