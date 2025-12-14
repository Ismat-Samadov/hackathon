"""
Pydantic models for API request/response schemas.

This module defines all request and response models used by the API endpoints.
Models are organized by feature area: OCR, Chat, and Knowledge Base.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# OCR Models
# ============================================================================

class PageOCR(BaseModel):
    """OCR result for a single page from a PDF document."""

    page_number: int = Field(
        ...,
        gt=0,
        description="Page number (1-indexed)"
    )
    MD_text: str = Field(
        ...,
        description="Extracted text in Markdown format"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "page_number": 1,
                "MD_text": "# Document Title\n\nExtracted content..."
            }
        }


class OCRResponse(BaseModel):
    """Response from OCR endpoint with all processed pages."""

    pages: List[PageOCR] = Field(
        default_factory=list,
        description="List of extracted pages"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages processed"
    )
    filename: str = Field(..., description="Original PDF filename")


# ============================================================================
# Chat Models
# ============================================================================

class ChatMessage(BaseModel):
    """A single message in the chat conversation."""

    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Message content"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What information is available?"
            }
        }


class Source(BaseModel):
    """A source reference from the knowledge base."""

    pdf_name: str = Field(
        ...,
        description="Name of the source PDF document"
    )
    page_number: int = Field(
        ...,
        gt=0,
        description="Page number in the PDF"
    )
    content: str = Field(
        ...,
        description="Relevant extracted text from the source"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "pdf_name": "document.pdf",
                "page_number": 1,
                "content": "Relevant text snippet..."
            }
        }


class ChatResponse(BaseModel):
    """Response from the chat endpoint with answer and sources."""

    sources: List[Source] = Field(
        default_factory=list,
        description="Retrieved source documents used to generate the answer"
    )
    answer: str = Field(
        ...,
        description="Generated answer to the user's query"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "sources": [
                    {
                        "pdf_name": "doc.pdf",
                        "page_number": 1,
                        "content": "..."
                    }
                ],
                "answer": "Based on the sources, ..."
            }
        }


# ============================================================================
# Knowledge Base Models
# ============================================================================

class Document(BaseModel):
    """A document stored in the knowledge base."""

    pdf_name: str = Field(..., description="Source PDF filename")
    page_number: int = Field(..., gt=0, description="Page number in PDF")
    content: str = Field(..., description="Document text content")
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding of the document"
    )


class KnowledgeBaseStatus(BaseModel):
    """Status summary of the knowledge base."""

    documents_count: int = Field(
        ...,
        ge=0,
        description="Total number of documents in the knowledge base"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages across all documents"
    )
    documents: List[dict] = Field(
        default_factory=list,
        description="List of documents with metadata"
    )
