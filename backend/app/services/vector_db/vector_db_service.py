"""
Qdrant vector database service.
Handles all vector storage and retrieval operations.
"""

import uuid
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import app_logger
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import (Distance, FieldCondition, Filter, MatchValue,
                                  PointStruct, SearchParams, VectorParams)


class VectorDBService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None,
        vector_dimension: int = None,
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection
            vector_dimension: Dimension of vectors
        """
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.vector_dimension = vector_dimension or settings.vector_dimension
        self.logger = app_logger
        
        # Initialize client
        try:
            self.client = QdrantClient(host=self.host, port=self.port, timeout=30)
            self.logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
            self._ensure_collection_exists()
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                self.logger.info(f"Collection {self.collection_name} created successfully")
            else:
                self.logger.info(f"Collection {self.collection_name} already exists")
        
        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    async def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector database.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadata: List of metadata dicts for each chunk
            ids: Optional list of IDs (generated if not provided)
            
        Returns:
            List of document IDs
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # Create points
            points = []
            for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                # Add text to metadata
                meta_with_text = {**meta, "text": text}
                
                point = PointStruct(
                    id=ids[i],
                    vector=embedding,
                    payload=meta_with_text,
                )
                points.append(point)
            
            # Upload points in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
            
            self.logger.info(f"Added {len(points)} documents to {self.collection_name}")
            return ids
        
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional filters (e.g., {"user_id": "123"})
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with text, metadata, and scores
        """
        try:
            # Build filter if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                query_filter = Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                })
            
            self.logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            raise
    
    async def delete_by_file_id(self, file_id: str) -> int:
        """
        Delete all documents associated with a file.
        
        Args:
            file_id: File ID to delete
            
        Returns:
            Number of documents deleted
        """
        try:
            # Delete points with matching file_id
            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="file_id",
                                match=MatchValue(value=file_id),
                            )
                        ]
                    )
                ),
            )
            
            self.logger.info(f"Deleted documents for file_id: {file_id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error deleting documents: {e}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Collection statistics
        """
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
                "vector_dimension": self.vector_dimension,
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            raise


# Global vector DB service instance
_vector_db_service = None


def get_vector_db_service() -> VectorDBService:
    """
    Get or create global vector DB service instance.
    
    Returns:
        VectorDBService instance
    """
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service
