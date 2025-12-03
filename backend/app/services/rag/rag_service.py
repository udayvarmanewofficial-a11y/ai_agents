"""
RAG (Retrieval-Augmented Generation) service.
Orchestrates document processing, embedding, storage, and retrieval.
"""

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import app_logger
from app.services.document_processor import get_document_processor
from app.services.embeddings import get_embedding_service
from app.services.vector_db import get_vector_db_service


class RAGService:
    """High-level RAG service for document management and retrieval."""
    
    def __init__(self):
        """Initialize RAG service with required components."""
        self.embedding_service = get_embedding_service()
        self.vector_db = get_vector_db_service()
        self.doc_processor = get_document_processor()
        self.logger = app_logger
    
    async def index_document(
        self,
        file_path: str,
        file_id: str,
        user_id: str,
        filename: str,
        file_type: str,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process and index a document into the vector database.
        
        Args:
            file_path: Path to the file
            file_id: Unique file identifier
            user_id: User identifier
            filename: Original filename
            file_type: File extension
            additional_metadata: Additional metadata to store
            
        Returns:
            Indexing results (chunks count, vector IDs, etc.)
        """
        try:
            self.logger.info(f"Starting document indexing for file: {filename}")
            
            # Extract text from document
            text = await self.doc_processor.process_file(file_path, file_type)
            
            if not text or len(text.strip()) < 10:
                raise ValueError("Document contains insufficient text content")
            
            # Create base metadata
            base_metadata = {
                "file_id": file_id,
                "user_id": user_id,
                "filename": filename,
                "file_type": file_type,
                **(additional_metadata or {}),
            }
            
            # Chunk the text
            chunks = self.doc_processor.chunk_text(text, metadata=base_metadata)
            self.logger.info(f"Document split into {len(chunks)} chunks")
            
            # Extract texts and metadata
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadata = [chunk["metadata"] for chunk in chunks]
            
            # Generate embeddings
            self.logger.info("Generating embeddings for chunks")
            embeddings = await self.embedding_service.encode_async(chunk_texts)
            embeddings_list = embeddings.tolist()
            
            # Store in vector database
            self.logger.info("Storing chunks in vector database")
            vector_ids = await self.vector_db.add_documents(
                texts=chunk_texts,
                embeddings=embeddings_list,
                metadata=chunk_metadata,
            )
            
            result = {
                "file_id": file_id,
                "chunks_count": len(chunks),
                "vector_ids": vector_ids,
                "total_characters": len(text),
                "status": "indexed",
            }
            
            self.logger.info(f"Document indexed successfully: {len(chunks)} chunks")
            return result
        
        except Exception as e:
            self.logger.error(f"Error indexing document: {e}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        user_id: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        score_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using RAG.
        
        Args:
            query: Search query
            top_k: Number of results to return
            user_id: Filter by user ID
            file_ids: Filter by specific file IDs
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            self.logger.info(f"Searching for: {query}")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.encode_async(query)
            query_embedding_list = query_embedding[0].tolist()
            
            # Build filters
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            
            # Search vector database
            results = await self.vector_db.search(
                query_embedding=query_embedding_list,
                top_k=top_k,
                filters=filters,
                score_threshold=score_threshold,
            )
            
            # Filter by file_ids if provided
            if file_ids:
                results = [r for r in results if r["metadata"].get("file_id") in file_ids]
            
            self.logger.info(f"Search returned {len(results)} results")
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            raise
    
    async def delete_document(self, file_id: str) -> bool:
        """
        Delete all vectors associated with a document.
        
        Args:
            file_id: File identifier
            
        Returns:
            Success status
        """
        try:
            self.logger.info(f"Deleting document: {file_id}")
            await self.vector_db.delete_by_file_id(file_id)
            self.logger.info(f"Document deleted successfully: {file_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector collection.
        
        Returns:
            Collection statistics
        """
        try:
            stats = await self.vector_db.get_collection_info()
            return stats
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            raise
    
    def build_context_from_results(
        self,
        results: List[Dict[str, Any]],
        max_length: int = 4000,
    ) -> str:
        """
        Build context string from search results for LLM.
        
        Args:
            results: Search results
            max_length: Maximum context length in characters
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            text = result["text"]
            filename = result["metadata"].get("filename", "Unknown")
            chunk_index = result["metadata"].get("chunk_index", "")
            
            part = f"[Source {i+1}: {filename}, Chunk {chunk_index}]\n{text}\n"
            
            if current_length + len(part) > max_length:
                break
            
            context_parts.append(part)
            current_length += len(part)
        
        if not context_parts:
            return "No relevant information found."
        
        return "\n".join(context_parts)


# Global RAG service instance
_rag_service = None


def get_rag_service() -> RAGService:
    """
    Get or create global RAG service instance.
    
    Returns:
        RAGService instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
