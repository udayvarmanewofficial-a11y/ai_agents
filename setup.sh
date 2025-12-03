#!/bin/bash

# Multi-Agent Planner Setup Script
# This script helps set up the application for first-time use

set -e

echo "🚀 Multi-Agent Planner Setup"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY (for OpenAI GPT models)"
    echo "   - GOOGLE_API_KEY (for Google Gemini models)"
    echo "   - Update POSTGRES_PASSWORD for security"
    echo "   - Update SECRET_KEY for security"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "📱 Application URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Qdrant:    http://localhost:6333/dashboard"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Create your first planning task"
    echo "   3. Upload documents to build your knowledge base"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs:      docker-compose logs -f"
    echo "   Stop services:  docker-compose down"
    echo "   Restart:        docker-compose restart"
    echo ""
else
    echo ""
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
