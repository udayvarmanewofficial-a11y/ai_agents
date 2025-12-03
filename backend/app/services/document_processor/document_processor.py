"""
Document processing and chunking service.
Handles file parsing, text extraction, and intelligent chunking.
"""

import os
import re
from pathlib import Path
from typing import Any, BinaryIO, Dict, List

import pypdf
import tiktoken
from app.core.config import settings
from app.core.logging import app_logger
from docx import Document as DocxDocument


class DocumentProcessor:
    """Service for processing and chunking documents."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.logger = app_logger
        
        # Initialize tokenizer for more accurate chunking
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            self.logger.warning(f"Failed to load tiktoken: {e}. Using character-based chunking.")
            self.tokenizer = None
    
    async def process_file(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a file.
        
        Args:
            file_path: Path to the file
            file_type: Type of file (.pdf, .txt, .md, .docx)
            
        Returns:
            Extracted text content
        """
        try:
            file_type = file_type.lower()
            
            if file_type == ".pdf":
                return await self._extract_pdf(file_path)
            elif file_type in [".txt", ".md"]:
                return await self._extract_text(file_path)
            elif file_type in [".doc", ".docx"]:
                return await self._extract_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    async def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text_parts = []
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            self.logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
        
        except Exception as e:
            self.logger.error(f"Error extracting PDF: {e}")
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text or markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            self.logger.info(f"Extracted {len(text)} characters from text file")
            return text
        
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            raise
    
    async def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = DocxDocument(file_path)
            text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(text_parts)
            
            self.logger.info(f"Extracted {len(full_text)} characters from DOCX")
            return full_text
        
        except Exception as e:
            self.logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        try:
            # Clean text
            text = self._clean_text(text)
            
            # Use recursive character splitting
            chunks = self._recursive_character_split(text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                }
                
                chunk_objects.append({
                    "text": chunk,
                    "metadata": chunk_metadata,
                })
            
            self.logger.info(f"Created {len(chunk_objects)} chunks from text")
            return chunk_objects
        
        except Exception as e:
            self.logger.error(f"Error chunking text: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def _recursive_character_split(self, text: str) -> List[str]:
        """
        Recursively split text using multiple separators.
        Tries to split at natural boundaries (paragraphs, sentences, etc.).
        """
        # Separators in order of preference
        separators = [
            "\n\n",  # Paragraphs
            "\n",    # Lines
            ". ",    # Sentences
            "! ",    # Sentences
            "? ",    # Sentences
            "; ",    # Clauses
            ", ",    # Phrases
            " ",     # Words
            "",      # Characters
        ]
        
        return self._split_text_recursive(text, separators)
    
    def _split_text_recursive(
        self,
        text: str,
        separators: List[str],
    ) -> List[str]:
        """Recursively split text using the provided separators."""
        if not text:
            return []
        
        # Base case: if text is small enough, return it
        if len(text) <= self.chunk_size:
            return [text] if text else []
        
        # Try each separator
        for i, separator in enumerate(separators):
            if separator == "":
                # Last resort: split by characters
                return self._split_by_characters(text)
            
            if separator in text:
                splits = text.split(separator)
                
                # Reconstruct chunks
                chunks = []
                current_chunk = ""
                
                for split in splits:
                    # Add separator back (except for last split)
                    split_with_sep = split + separator if split != splits[-1] else split
                    
                    if len(current_chunk) + len(split_with_sep) <= self.chunk_size:
                        current_chunk += split_with_sep
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        
                        # If split is too large, recursively split it
                        if len(split_with_sep) > self.chunk_size:
                            sub_chunks = self._split_text_recursive(
                                split_with_sep,
                                separators[i + 1:],
                            )
                            chunks.extend(sub_chunks)
                            current_chunk = ""
                        else:
                            current_chunk = split_with_sep
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Apply overlap
                return self._apply_overlap(chunks)
        
        return [text]
    
    def _split_by_characters(self, text: str) -> List[str]:
        """Split text by characters as last resort."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between chunks."""
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks
        
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]
            
            # Get overlap from previous chunk
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
            
            # Combine overlap with current chunk
            combined_chunk = overlap_text + " " + current_chunk
            overlapped_chunks.append(combined_chunk)
        
        return overlapped_chunks


# Global document processor instance
_document_processor = None


def get_document_processor() -> DocumentProcessor:
    """
    Get or create global document processor instance.
    
    Returns:
        DocumentProcessor instance
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
