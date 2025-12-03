"""
Main FastAPI application.
"""

import time
from contextlib import asynccontextmanager

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import app_logger
from app.db import init_db
from app.db.migrations import run_migrations
from app.schemas import HealthResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    app_logger.info("Starting Multi-Agent Planner API")
    app_logger.info(f"Environment: {settings.environment}")
    
    # Initialize database
    try:
        init_db()
        app_logger.info("Database initialized successfully")
        
        # Run migrations to ensure schema is up to date
        run_migrations()
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {e}")
    
    # Initialize services (they will be lazy-loaded on first use)
    app_logger.info("Services ready for initialization on demand")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down Multi-Agent Planner API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-Agent Planning System with RAG capabilities",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime

    # Check service health
    services_status = {
        "database": "healthy",  # Could add actual checks
        "vector_db": "healthy",
        "llm": "healthy",
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        services=services_status,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


# Include API router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
        log_level=settings.log_level.lower(),
    )
