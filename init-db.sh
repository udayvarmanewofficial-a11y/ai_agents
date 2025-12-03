#!/bin/bash
#Initialize database by running migrations from inside the PostgreSQL container

echo "🗄️  Initializing database..."

# Copy alembic files into container
docker cp backend/alembic planner-postgres-dev:/tmp/
docker cp backend/app planner-postgres-dev:/tmp/
docker cp backend/.env planner-postgres-dev:/tmp/

# Install Python and dependencies in container
docker exec planner-postgres-dev sh -c "
apk add --no-cache python3 py3-pip &&
pip3 install alembic sqlalchemy psycopg2-binary pydantic pydantic-settings &&
cd /tmp &&
export PYTHONPATH=/tmp &&
export DATABASE_URL=postgresql://postgres@localhost:5432/planner_db &&
# Create database if it doesn't exist
psql -U postgres -c 'CREATE DATABASE planner_db;' 2>/dev/null || true &&
# Generate and run migrations
cd /tmp && alembic -c /tmp/alembic.ini revision --autogenerate -m 'Initial migration' &&
alembic -c /tmp/alembic.ini upgrade head
"

echo "✅ Database initialized!"
