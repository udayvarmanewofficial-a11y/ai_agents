# Local Development Setup

This guide explains how to run the application locally without Docker for faster development.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (only for supporting services: PostgreSQL, Redis, Qdrant)
- Optional: tmux (for running both servers in one terminal)

## Quick Start

### 1. Initial Setup

Run the setup script to configure your development environment:

```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

This will:

- Create Python virtual environment
- Install all Python dependencies
- Install Node.js dependencies
- Create `.env` file
- Create run scripts

### 2. Configure Environment

Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=your-actual-key
GOOGLE_API_KEY=your-actual-key
```

### 3. Start Supporting Services

Start only the required database services using Docker:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This starts:

- PostgreSQL on port 5432
- Redis on port 6379
- Qdrant on port 6333

### 4. Initialize Database

Run database migrations:

```bash
./setup-db-dev.sh
```

### 5. Start Development Servers

**Option A: Using tmux (both servers in one terminal)**

```bash
./run-dev.sh
```

- Press `Ctrl+B` then `D` to detach from tmux
- Run `tmux attach -t planner-dev` to reattach

**Option B: Separate terminals**

Terminal 1 (Backend):

```bash
./run-backend-dev.sh
```

Terminal 2 (Frontend):

```bash
./run-frontend-dev.sh
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development Workflow

### Making Changes

**Backend Changes:**

- Edit files in `backend/app/`
- Server auto-reloads on file changes (thanks to `--reload` flag)
- No rebuild needed!

**Frontend Changes:**

- Edit files in `frontend/src/`
- Hot module replacement updates browser instantly
- No rebuild needed!

### Running Tests

**Backend Tests:**

```bash
cd backend
source venv/bin/activate
pytest
```

**Frontend Tests:**

```bash
cd frontend
npm test
```

### Adding Dependencies

**Python Packages:**

```bash
cd backend
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

**Node Packages:**

```bash
cd frontend
npm install package-name
```

## Common Issues

### Port Already in Use

If you get "port already in use" errors:

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Connection Issues

Make sure Docker services are running:

```bash
docker-compose -f docker-compose.dev.yml ps
```

Restart services if needed:

```bash
docker-compose -f docker-compose.dev.yml restart
```

### Python Virtual Environment Issues

Recreate the virtual environment:

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Switching Between Dev and Production

### Local Development (Current Setup)

- Fast iteration
- No Docker rebuilds for code changes
- Services: `docker-compose -f docker-compose.dev.yml up -d`

### Production/Docker Mode

- Full Docker deployment
- All services containerized
- Services: `docker-compose up -d`

## Stopping Services

### Stop Development Servers

- Press `Ctrl+C` in each terminal
- Or if using tmux: `tmux kill-session -t planner-dev`

### Stop Docker Services

```bash
docker-compose -f docker-compose.dev.yml down
```

## Clean Restart

```bash
# Stop everything
docker-compose -f docker-compose.dev.yml down -v
pkill -f uvicorn
pkill -f vite

# Start fresh
docker-compose -f docker-compose.dev.yml up -d
./setup-db-dev.sh
./run-dev.sh
```

## Performance Tips

1. **Use tmux or multiple terminals** - Easier to manage both servers
2. **Keep Docker services running** - No need to stop/start between sessions
3. **Watch logs in separate terminal**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

## Advantages of This Setup

✅ **Instant Feedback** - Code changes reflected immediately
✅ **Faster Iteration** - No Docker rebuilds
✅ **Better Debugging** - Direct access to Python debugger
✅ **Resource Efficient** - Only DB services in Docker
✅ **IDE Integration** - Full IntelliSense and debugging support
✅ **Easy Testing** - Run tests directly in your environment

## Need Help?

- Check backend logs: Look in terminal running `run-backend-dev.sh`
- Check frontend logs: Look in terminal running `run-frontend-dev.sh`
- Check Docker services: `docker-compose -f docker-compose.dev.yml logs`
- Database issues: `./setup-db-dev.sh` to reset migrations
