"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"


class TaskType(str, Enum):
    """Types of planning tasks."""
    EXAM_PREPARATION = "exam_preparation"
    PROJECT_PLANNING = "project_planning"
    LEARNING_PATH = "learning_path"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Task processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"


class TaskCreateRequest(BaseModel):
    """Request schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(..., min_length=10, description="Detailed task description")
    task_type: TaskType = Field(..., description="Type of planning task")
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider to use")
    model_name: Optional[str] = Field(None, description="Specific model name (optional)")
    use_custom_rag: bool = Field(default=False, description="Force use of custom RAG data only")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Prepare for Python Certification Exam",
                "description": "I need to prepare for the Python PCAP certification exam in 2 months. I have basic Python knowledge and can dedicate 2 hours daily.",
                "task_type": "exam_preparation",
                "llm_provider": "openai",
                "model_name": "gpt-4-turbo-preview"
            }
        }


class TaskResponse(BaseModel):
    """Response schema for task information."""
    id: str
    user_id: str
    title: str
    description: str
    task_type: str
    status: str
    llm_provider: str
    model_name: str
    use_custom_rag: bool = False  # Will be converted from int (0/1) to bool
    research_output: Optional[Dict[str, Any]] = None
    plan_output: Optional[Dict[str, Any]] = None
    review_output: Optional[Dict[str, Any]] = None
    final_output: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    @validator('use_custom_rag', pre=True)
    def convert_int_to_bool(cls, v):
        """Convert database int (0/1) to boolean."""
        if isinstance(v, int):
            return bool(v)
        return v
    
    class Config:
        from_attributes = True


class TaskModifyRequest(BaseModel):
    """Request schema for modifying a task/plan."""
    modification_request: str = Field(..., min_length=10, description="What changes to make")
    llm_provider: Optional[LLMProvider] = Field(None, description="LLM provider to use for modification")
    model_name: Optional[str] = Field(None, description="Specific model name for modification")
    use_custom_rag: Optional[bool] = Field(None, description="Force use of custom RAG data only")
    
    class Config:
        json_schema_extra = {
            "example": {
                "modification_request": "Add more focus on object-oriented programming concepts and reduce the time spent on basic syntax.",
                "llm_provider": "gemini",
                "model_name": "gemini-2.5-pro",
                "use_custom_rag": True
            }
        }


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""
    file_id: str = Field(alias="id")
    filename: str
    file_size_bytes: int
    status: str
    chunks_count: int = 0
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class FileInfo(BaseModel):
    """Information about an uploaded file."""
    id: str
    filename: str
    original_filename: str
    file_size_bytes: int
    file_type: str
    status: str
    chunks_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RAGSearchRequest(BaseModel):
    """Request schema for RAG search."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key concepts in object-oriented programming?",
                "top_k": 5
            }
        }


class RAGSearchResult(BaseModel):
    """Single search result from RAG."""
    text: str
    score: float
    metadata: Dict[str, Any]
    file_id: Optional[str] = None
    filename: Optional[str] = None


class RAGSearchResponse(BaseModel):
    """Response schema for RAG search."""
    query: str
    results: List[RAGSearchResult]
    total_results: int


class AgentProgress(BaseModel):
    """Real-time agent progress update."""
    task_id: str
    agent_type: str
    status: str
    message: str
    progress_percentage: float = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
