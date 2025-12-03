# 🚀 Quick Setup Guide

## One-Time Setup (5 minutes)

### Step 1: Run Setup Script

```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

This installs all dependencies and creates configuration files.

### Step 2: Start Database Services

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Note:** Uses PostgreSQL on port **54320** (not 5432) to avoid conflicts with local installations.

### Step 3: Initialize Database

```bash
python3 init-db.py
```

Creates all required database tables.

### Step 4: Add API Keys (Required for LLM functionality)

Edit `.env` file in the **root directory** and add your **real** API keys:

```bash
# Get OpenAI key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-real-key-here

# Get Gemini key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-real-key-here
```

**Note:** The backend reads from the root `.env` file - no need to copy it anywhere!

**You need at least ONE of these keys for the app to work!**

## Running the App

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

## Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Troubleshooting

### Port 5432 Already in Use

If you have local PostgreSQL running, don't worry! This setup uses port **54320** instead.

### Database Connection Error

```bash
# Restart database services
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
python3 init-db.py
```

### Backend Won't Start

```bash
# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9
```

## That's It! 🎉

Your multi-agent planning system is ready to use!
