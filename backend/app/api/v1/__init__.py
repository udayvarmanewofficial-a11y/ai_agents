"""
API v1 router initialization.
"""

from app.api.v1 import rag, tasks
from fastapi import APIRouter

api_router = APIRouter()

# Include sub-routers
api_router.include_router(tasks.router)
api_router.include_router(rag.router)
