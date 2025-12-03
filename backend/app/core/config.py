"""
Core configuration settings for the application.
Loads environment variables and provides typed configuration objects.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Multi-Agent Planner"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Backend API
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = True
    
    # LLM Providers - OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096
    
    # LLM Providers - Google Gemini
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 8192
    
    # Default LLM Provider
    default_llm_provider: str = "gemini"
    
    # Vector Database - Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "knowledge_base"
    vector_dimension: int = 384
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 100
    allowed_file_extensions: str = ".pdf,.txt,.md,.doc,.docx"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Database (PostgreSQL)
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 54320
    postgres_db: str = "planner_db"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    
    # Authentication
    secret_key: str = "your_secret_key_here_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # File Upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert allowed extensions string to list."""
        return [ext.strip() for ext in self.allowed_file_extensions.split(",")]
    
    @property
    def database_url(self) -> str:
        """PostgreSQL database URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = "../.env"  # Read from root directory .env file
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
