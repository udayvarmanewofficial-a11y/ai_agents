# Makefile for Multi-Agent Planner

.PHONY: help build up down logs restart clean test backend-dev frontend-dev

help:
	@echo "Multi-Agent Planner - Available Commands"
	@echo ""
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Remove containers, volumes, and images"
	@echo "  make test           - Run tests"
	@echo "  make backend-dev    - Start backend in development mode"
	@echo "  make frontend-dev   - Start frontend in development mode"
	@echo ""

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v --rmi all
	rm -rf backend/__pycache__
	rm -rf backend/**/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf uploads/*
	rm -rf qdrant_data/*

# Development commands
backend-dev:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm run dev

# Testing
test:
	cd backend && pytest

# Database
db-migrate:
	cd backend && alembic upgrade head

db-reset:
	docker-compose down postgres
	docker volume rm planner-llm_postgres_data
	docker-compose up -d postgres
	sleep 5
	cd backend && alembic upgrade head

# Installation
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installation complete!"

# Setup
setup: install
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file. Please update with your API keys."; fi
	@echo "Setup complete!"
