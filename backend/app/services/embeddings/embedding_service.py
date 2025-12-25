"""
Embedding service for generating vector embeddings.
Uses sentence-transformers for local embeddings or OpenAI for cloud-based.
"""

from typing import List, Union

import numpy as np
from app.core.config import settings
from app.core.logging import app_logger


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize embedding service.
        
        Args:
            model_name: Name of the embedding model
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.model_name = model_name or settings.embedding_model
        self.device = device or settings.embedding_device
        self.logger = app_logger
        
        # Load the embedding model (lazy import to avoid startup issues)
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            # Import here to avoid loading heavy dependencies at module import time
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Embedding model loaded. Dimension: {self.dimension}")
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing multiple texts
            
        Returns:
            Numpy array of embeddings
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True,
            )
            
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def encode_async(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Async version of encode (runs in thread pool).
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        import asyncio
        from functools import partial
        
        loop = asyncio.get_event_loop()
        encode_func = partial(self.encode, texts=texts, batch_size=batch_size)
        embeddings = await loop.run_in_executor(None, encode_func)
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.dimension


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create global embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
