"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Section(BaseModel):
    """Represents a document section."""
    id: int
    title: str
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    page_number: Optional[int] = None
    features: Dict[str, Any] = {}
    tags: List[str] = []


class DocumentResult(BaseModel):
    """Result of document processing."""
    document_id: str
    document_name: str
    total_sections: int
    relevant_sections: int
    sections: List[Section]
    processing_time: float
    threshold: float = 0.5


class UploadResponse(BaseModel):
    """Response for document upload."""
    document_id: str
    filename: str
    status: str
    message: str


class FeedbackRequest(BaseModel):
    """Request to submit section feedback."""
    document_id: str
    section_id: int
    is_relevant: bool


class FeedbackResponse(BaseModel):
    """Response for feedback submission."""
    status: str
    message: str


class BatchUploadRequest(BaseModel):
    """Request for batch processing."""
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    min_section_length: int = Field(default=20, ge=1)


class BatchUploadResponse(BaseModel):
    """Response for batch upload."""
    document_ids: List[str]
    total_documents: int
    status: str


class ExportRequest(BaseModel):
    """Request to export results."""
    document_id: str
    format: str = Field(default='json', pattern='^(json|txt)$')
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    spacy_model: Optional[str] = None
    model_trained: bool = False
