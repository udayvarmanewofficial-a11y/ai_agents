#!/bin/bash

# Local Development Setup Script
# This script sets up a local development environment without Docker

set -e

echo "🚀 Setting up local development environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Backend Setup
echo -e "\n${BLUE}Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ ! -f venv/bin/activate ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads logs

cd ..

# Frontend Setup
echo -e "\n${BLUE}Setting up Frontend...${NC}"
cd frontend

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "Node modules already installed. Run 'npm install' if you need to update."
fi

cd ..

# Create/Update .env file
echo -e "\n${BLUE}Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo "Creating .env file with default configuration..."
    cat > .env << 'EOF'
# Application Settings
APP_NAME=Multi-Agent Planner
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Backend API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=true

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000

# LLM Providers - OpenAI (Get your key from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your-real-openai-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# LLM Providers - Google Gemini (Get your key from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your-real-google-key-here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Default LLM Provider (openai or gemini)
DEFAULT_LLM_PROVIDER=openai

# Vector Database - Qdrant
QDRANT_HOST=127.0.0.1
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=knowledge_base
VECTOR_DIMENSION=384

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_EXTENSIONS=.pdf,.txt,.md,.doc,.docx

# Redis (for caching and job queue)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://127.0.0.1:6379

# Database (PostgreSQL) - Using port 54320 to avoid conflict with local PostgreSQL
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54320
POSTGRES_DB=planner_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
DATABASE_URL=postgresql://postgres@127.0.0.1:54320/planner_db

# Authentication
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF
    echo -e "${GREEN}✅ .env file created with default configuration${NC}"
    echo -e "${YELLOW}⚠️  Remember to add your real API keys for OpenAI/Gemini later!${NC}"
else
    echo ".env file already exists - skipping"
fi

# Check for required services
echo -e "\n${BLUE}Checking required services...${NC}"
echo "The following services need to be running:"
echo "  - PostgreSQL (port 5432)"
echo "  - Redis (port 6379)"
echo "  - Qdrant (port 6333)"
echo ""
echo "You can start these services using:"
echo "  ${GREEN}docker-compose up -d postgres redis qdrant${NC}"

# Create run scripts
echo -e "\n${BLUE}Creating run scripts...${NC}"

# Backend run script
cat > run-backend-dev.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
export PYTHONPATH=$PWD
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x run-backend-dev.sh

# Frontend run script
cat > run-frontend-dev.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
chmod +x run-frontend-dev.sh

# Combined run script
cat > run-dev.sh << 'EOF'
#!/bin/bash

# Run both backend and frontend in local dev mode
# Requires tmux to be installed

if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Install it with: brew install tmux"
    echo ""
    echo "Or run services separately:"
    echo "  Terminal 1: ./run-backend-dev.sh"
    echo "  Terminal 2: ./run-frontend-dev.sh"
    exit 1
fi

# Create a new tmux session
SESSION="planner-dev"

tmux new-session -d -s $SESSION

# Split window
tmux split-window -h -t $SESSION

# Run backend in left pane
tmux send-keys -t $SESSION:0.0 './run-backend-dev.sh' C-m

# Run frontend in right pane
tmux send-keys -t $SESSION:0.1 './run-frontend-dev.sh' C-m

# Attach to session
echo "Starting development servers in tmux session..."
echo "Use Ctrl+B then D to detach, 'tmux attach -t planner-dev' to reattach"
sleep 2
tmux attach -t $SESSION
EOF
chmod +x run-dev.sh

# Database setup script
cat > setup-db-dev.sh << 'EOF'
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
EOF
chmod +x setup-db-dev.sh

echo -e "\n${GREEN}✅ Local development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}🚀 Quick Start (3 simple steps):${NC}"
echo ""
echo "1. ${YELLOW}⚠️  IMPORTANT: Add your API keys in .env file${NC}"
echo "   Get OpenAI key: ${GREEN}https://platform.openai.com/api-keys${NC}"
echo "   Get Gemini key: ${GREEN}https://makersuite.google.com/app/apikey${NC}"
echo ""
echo "2. Start database services:"
echo "   ${GREEN}docker-compose -f docker-compose.dev.yml up -d${NC}"
echo ""
echo "3. Initialize database tables:"
echo "   ${GREEN}python3 init-db.py${NC}"
echo ""
echo "4. Run development servers:"
echo "   ${GREEN}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}  (Terminal 1)"
echo "   ${GREEN}cd frontend && npm run dev${NC}  (Terminal 2)"
echo ""
echo -e "${BLUE}📝 Access:${NC}"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}📌 Note:${NC} Using PostgreSQL on port ${GREEN}54320${NC} (not 5432) to avoid conflicts"
echo ""
