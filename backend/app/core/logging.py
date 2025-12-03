"""
Logging configuration using loguru.
Provides structured logging with rotation and JSON formatting.
"""

import sys

from app.core.config import settings
from loguru import logger


def setup_logging():
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with appropriate level
    log_level = settings.log_level.upper()
    
    if settings.log_format == "json":
        # JSON format for production
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
            level=log_level,
            serialize=True,
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
        )
    
    # File handler with rotation
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
    )
    
    logger.info(f"Logging configured with level: {log_level}")
    
    return logger


# Global logger instance
app_logger = setup_logging()
