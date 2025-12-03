"""
RAG (file upload and search) API endpoints.
"""

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.core.logging import app_logger
from app.db import get_db
from app.models import UploadedFile
from app.schemas import (FileInfo, FileUploadResponse, RAGSearchRequest,
                         RAGSearchResponse, RAGSearchResult)
from app.services.rag import get_rag_service
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = "default_user",  # TODO: Get from auth
):
    """
    Upload a file and index it in the RAG system.
    
    Args:
        file: Uploaded file
        db: Database session
        user_id: User identifier
        
    Returns:
        File upload information
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {settings.allowed_file_extensions}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB"
            )
        
        # Create file entry in database
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        
        # Ensure upload directory exists
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database entry
        uploaded_file = UploadedFile(
            id=file_id,
            user_id=user_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            file_type=file_ext,
            mime_type=file.content_type,
            status="uploaded",
        )
        
        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)
        
        # Index the file asynchronously
        try:
            rag_service = get_rag_service()
            indexing_result = await rag_service.index_document(
                file_path=str(file_path),
                file_id=file_id,
                user_id=user_id,
                filename=file.filename,
                file_type=file_ext,
            )
            
            # Update file status
            uploaded_file.status = "indexed"
            uploaded_file.chunks_count = indexing_result["chunks_count"]
            uploaded_file.vector_ids = indexing_result["vector_ids"]
            uploaded_file.processed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(uploaded_file)
            
            app_logger.info(f"File uploaded and indexed: {file_id}")
        
        except Exception as e:
            app_logger.error(f"Error indexing file {file_id}: {e}")
            uploaded_file.status = "failed"
            uploaded_file.error_message = str(e)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error indexing file: {str(e)}")
        
        return FileUploadResponse.model_validate(uploaded_file)
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error uploading file: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=RAGSearchResponse)
async def search_documents(
    request: RAGSearchRequest,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Search for relevant documents in the RAG system.
    
    Args:
        request: Search request
        db: Database session
        user_id: User identifier
        
    Returns:
        Search results
    """
    try:
        rag_service = get_rag_service()
        
        # Perform search
        results = await rag_service.search(
            query=request.query,
            top_k=request.top_k,
            user_id=request.user_id or user_id,
        )
        
        # Format results
        formatted_results = [
            RAGSearchResult(
                text=result["text"],
                score=result["score"],
                metadata=result["metadata"],
                file_id=result["metadata"].get("file_id"),
                filename=result["metadata"].get("filename"),
            )
            for result in results
        ]
        
        return RAGSearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
        )
    
    except Exception as e:
        app_logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=List[FileInfo])
async def list_files(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    List all uploaded files for a user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        user_id: User identifier
        
    Returns:
        List of files
    """
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == user_id
    ).order_by(UploadedFile.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    return [FileInfo.model_validate(f) for f in files]


@router.get("/files/{file_id}", response_model=FileInfo)
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Get file information by ID.
    
    Args:
        file_id: File identifier
        db: Database session
        user_id: User identifier
        
    Returns:
        File information
    """
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == user_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileInfo.model_validate(file)


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Delete a file and its vectors from the RAG system.
    
    Args:
        file_id: File identifier
        db: Database session
        user_id: User identifier
        
    Returns:
        Success message
    """
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == user_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete from vector database
        rag_service = get_rag_service()
        await rag_service.delete_document(file_id)
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete from database
        db.delete(file)
        db.commit()
        
        app_logger.info(f"File deleted: {file_id}")
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        app_logger.error(f"Error deleting file {file_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_rag_stats(
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Get RAG system statistics.
    
    Args:
        db: Database session
        user_id: User identifier
        
    Returns:
        Statistics about the RAG system
    """
    try:
        # Get user file stats
        total_files = db.query(UploadedFile).filter(
            UploadedFile.user_id == user_id
        ).count()
        
        indexed_files = db.query(UploadedFile).filter(
            UploadedFile.user_id == user_id,
            UploadedFile.status == "indexed"
        ).count()
        
        total_chunks = db.query(UploadedFile).filter(
            UploadedFile.user_id == user_id,
            UploadedFile.status == "indexed"
        ).with_entities(UploadedFile.chunks_count).all()
        
        total_chunks_count = sum([c[0] for c in total_chunks if c[0]])
        
        # Get collection stats
        rag_service = get_rag_service()
        collection_stats = await rag_service.get_collection_stats()
        
        return {
            "user_stats": {
                "total_files": total_files,
                "indexed_files": indexed_files,
                "total_chunks": total_chunks_count,
            },
            "collection_stats": collection_stats,
        }
    
    except Exception as e:
        app_logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
