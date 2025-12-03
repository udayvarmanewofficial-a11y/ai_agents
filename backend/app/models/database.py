"""
Database models for PostgreSQL using SQLAlchemy.
Stores metadata about tasks, files, and user sessions.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    """Task processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"


class AgentType(str, enum.Enum):
    """Agent types in the system."""
    RESEARCHER = "researcher"
    PLANNER = "planner"
    REVIEWER = "reviewer"


class Task(Base):
    """Task table for storing planning tasks."""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String, nullable=False)  # e.g., "exam_preparation", "project_planning"
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
    # LLM configuration
    llm_provider = Column(String, nullable=False)  # "openai" or "gemini"
    model_name = Column(String, nullable=False)
    use_custom_rag = Column(Integer, default=0, nullable=False)  # Use Integer for SQLite boolean compatibility (0=False, 1=True)
    
    # Results from agents
    research_output = Column(JSON, nullable=True)
    plan_output = Column(JSON, nullable=True)
    review_output = Column(JSON, nullable=True)
    final_output = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent_logs = relationship("AgentLog", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class AgentLog(Base):
    """Logs for individual agent executions."""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    
    # Agent execution details
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    status = Column(String, nullable=False)  # "started", "completed", "failed"
    error_message = Column(Text, nullable=True)
    
    # Performance metrics
    execution_time_seconds = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="agent_logs")
    
    def __repr__(self):
        return f"<AgentLog(id={self.id}, task_id={self.task_id}, agent={self.agent_type}, status={self.status})>"


class UploadedFile(Base):
    """Metadata for uploaded files in RAG system."""
    __tablename__ = "uploaded_files"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded", nullable=False)  # "uploaded", "processing", "indexed", "failed"
    error_message = Column(Text, nullable=True)
    
    # Vector DB metadata
    chunks_count = Column(Integer, default=0, nullable=False)
    vector_ids = Column(JSON, nullable=True)  # List of vector IDs in Qdrant
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.filename}, status={self.status})>"


class UserSession(Base):
    """User session tracking."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    
    # Session metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
