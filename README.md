# Multi-Agent Planning System with RAG

A production-ready web application that leverages multiple AI agents (Researcher, Planner, Reviewer) to create comprehensive plans and schedules. Features a RAG (Retrieval-Augmented Generation) system for incorporating private knowledge bases.

## 🚀 Quick Start

### Option 1: Local Development (Fast & Easy)

**Best for development - instant code reloading, no Docker rebuilds**

```bash
# 1. One-time setup (installs dependencies, creates .env)
./setup-dev.sh

# 2. Start database services (PostgreSQL, Redis, Qdrant)
docker-compose -f docker-compose.dev.yml up -d

# 3. Initialize database
./setup-db-dev.sh

# 4. Run development servers
./run-backend-dev.sh   # Terminal 1
./run-frontend-dev.sh  # Terminal 2

# Or use tmux to run both:
./run-dev.sh
```

**Access:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

📖 **Detailed dev setup:** See [README-DEV.md](README-DEV.md)

### Option 2: Docker Production

**Full containerized deployment for production**

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add your API keys

# 2. Build and start all services
docker-compose up -d

# 3. Initialize database
docker-compose exec backend alembic upgrade head
```

**Access:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 🌟 Features

- **Multi-Agent System**: Three specialized AI agents work collaboratively

  - **Researcher Agent**: Gathers and analyzes information from your knowledge base
  - **Planner Agent**: Creates detailed, actionable plans and schedules
  - **Reviewer Agent**: Reviews and refines plans, handles modifications

- **RAG Knowledge Base**: Upload documents (PDF, TXT, MD, DOCX) to build a private knowledge base that agents can reference

- **Multi-Model Support**: Choose between OpenAI (GPT-4) and Google Gemini models

- **Real-time Progress**: Track agent progress as they work on your tasks

- **Interactive Modifications**: Request changes to generated plans with natural language

- **Production-Ready**: Dockerized deployment with proper separation of concerns

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   React     │────────▶│   FastAPI        │────────▶│   Qdrant    │
│   Frontend  │         │   Backend        │         │  Vector DB  │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │
                                ├──────▶ PostgreSQL (metadata)
                                ├──────▶ Redis (caching)
                                └──────▶ LLM Providers (OpenAI/Gemini)
```

### Agent Workflow

```
User Request
    │
    ▼
Researcher Agent ────┐
    │                │
    │                ▼
    └──────▶ Planner Agent ────┐
                 │              │
                 │              ▼
                 └──────▶ Reviewer Agent
                              │
                              ▼
                         Final Plan
```

## 📋 Prerequisites

### For Local Development

- **Python 3.11+**
- **Node.js 18+**
- **Docker** and **Docker Compose** (for database services only)
- **OpenAI API Key** and/or **Google API Key**
- At least **2GB RAM** available

### For Production Docker Deployment

- **Docker** and **Docker Compose** (v2.0+)
- **OpenAI API Key** and/or **Google API Key**
- At least **4GB RAM** and **10GB disk space**

## 🚀 Quick Start

## 💡 First Time Setup

### 1. Clone the Repository

```bash
git clone https://github.com/varmakarthik12/planner-llm.git
cd planner-llm
```

### 2. For Local Development (Recommended)

```bash
# Run the automated setup script
chmod +x setup-dev.sh
./setup-dev.sh

# ⚠️  IMPORTANT: Add your real API keys in .env file
# - OpenAI: https://platform.openai.com/api-keys
# - Gemini: https://makersuite.google.com/app/apikey
# Edit .env and replace:
#   OPENAI_API_KEY=your-real-openai-key-here
#   GOOGLE_API_KEY=your-real-google-key-here

# Start database services (uses port 54320 to avoid conflict with local PostgreSQL)
docker-compose -f docker-compose.dev.yml up -d

# Initialize database tables
python3 init-db.py

# Start backend (Terminal 1)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
cd frontend && npm run dev
```

**Access:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Note:** Default setup uses PostgreSQL on port **54320** (not 5432) to avoid conflicts with local PostgreSQL installations.

```env
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-key-here
```

## 📖 Usage Guide

### Creating a Planning Task

1. Click "**+ New Task**" on the Planning page
2. Fill in the task details:
   - **Title**: Short description of what you want to plan
   - **Description**: Detailed explanation including your goals, constraints, timeline, etc.
   - **Task Type**: Select the type (Exam Preparation, Project Planning, Learning Path, Custom)
   - **LLM Provider**: Choose OpenAI or Gemini
3. Click "**Create Task**"
4. The agents will start working immediately
5. Monitor progress and view results on the task detail page

### Using the Knowledge Base (RAG)

1. Navigate to the "**Knowledge Base**" tab
2. **Upload Documents**:
   - Drag and drop files or click to browse
   - Supported formats: PDF, TXT, MD, DOC, DOCX
   - Files are automatically processed and indexed
3. **Search Your Knowledge**:
   - Use the search box to test retrieval
   - View relevant chunks with similarity scores
4. **Agent Integration**:
   - Agents automatically query the knowledge base during research
   - Uploaded documents enhance plan quality with your specific information

### Modifying Plans

1. Open a completed task
2. Click "**Modify Plan**"
3. Describe your desired changes in natural language
4. The Reviewer Agent will update the plan accordingly

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

## 🏭 Production Deployment

### Building for Production

```bash
# Build all containers
docker-compose build

# Start in production mode
docker-compose up -d
```

### Environment Configuration

For production, update these critical settings in `.env`:

```env
ENVIRONMENT=production
DEBUG=false

# Use strong, unique passwords
POSTGRES_PASSWORD=<strong-password>
SECRET_KEY=<generate-strong-secret>

# Configure allowed origins
CORS_ORIGINS=https://yourdomain.com

# Use production-grade LLM settings
OPENAI_MODEL=gpt-4-turbo-preview
```

### Health Monitoring

Check service health:

```bash
# Backend health
curl http://localhost:8000/health

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📊 System Components

### Backend Services

- **FastAPI**: REST API and WebSocket server
- **SQLAlchemy**: ORM for PostgreSQL
- **Qdrant**: Vector database for embeddings
- **Redis**: Caching and job queue
- **Sentence Transformers**: Local embedding generation

### Frontend

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client
- **React Markdown**: Render agent outputs

## 🔧 Configuration Options

### LLM Providers

**OpenAI**:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

**Google Gemini**:

```env
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000
```

### RAG Configuration

```env
# Chunking strategy
CHUNK_SIZE=1000          # Characters per chunk
CHUNK_OVERLAP=200        # Overlap between chunks

# File upload limits
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_EXTENSIONS=.pdf,.txt,.md,.doc,.docx

# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION=384
```

### Database Configuration

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=planner_db
POSTGRES_USER=planner_user
POSTGRES_PASSWORD=your_password

QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=knowledge_base
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Ensure API keys are set in .env
# 2. Check database connectivity
docker-compose ps
```

### Vector DB connection issues

```bash
# Restart Qdrant
docker-compose restart qdrant

# Check Qdrant health
curl http://localhost:6333/health
```

### File upload fails

```bash
# Check upload directory permissions
mkdir -p uploads
chmod 755 uploads

# Check file size limits in .env
MAX_FILE_SIZE_MB=100
```

### Frontend can't connect to backend

```bash
# Check CORS settings in .env (root directory)
CORS_ORIGINS=http://localhost:3000

# Check API URL in frontend
# frontend/.env.local should have:
VITE_API_URL=http://localhost:8000
```

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Tasks**:

- `POST /api/v1/tasks/create` - Create a new planning task
- `GET /api/v1/tasks/{task_id}` - Get task details
- `POST /api/v1/tasks/{task_id}/modify` - Modify a task

**RAG**:

- `POST /api/v1/rag/upload` - Upload document
- `POST /api/v1/rag/search` - Search knowledge base
- `GET /api/v1/rag/files` - List uploaded files

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Google for Gemini models
- Qdrant for vector database
- FastAPI framework
- React community

## 📧 Support

For issues and questions:

- GitHub Issues: https://github.com/varmakarthik12/planner-llm/issues
- Documentation: See `docs/` directory

---

Built with ❤️ for students and learners
