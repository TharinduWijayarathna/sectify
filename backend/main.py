"""
FastAPI main application for document section extraction.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import shutil
import time
from pathlib import Path
import logging

from document_parser import DocumentParser
from section_segmenter import SectionSegmenter
from feature_extractor import FeatureExtractor
from relevance_classifier import RelevanceClassifier
from models import (
    DocumentResult, Section, UploadResponse, FeedbackRequest,
    FeedbackResponse, HealthResponse, ExportRequest
)
from utils import (
    setup_logging, validate_file_type, generate_document_id,
    format_error_response, ensure_dir, load_spacy_model
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Section Extraction API",
    description="NLP-powered system for extracting relevant sections from documents",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
UPLOAD_DIR = ensure_dir("./uploads")
MODEL_DIR = ensure_dir("./models")

# Initialize components
nlp = load_spacy_model("en_core_web_sm")
parser = DocumentParser()
segmenter = SectionSegmenter(min_section_length=20)
feature_extractor = FeatureExtractor(nlp=nlp)
classifier = RelevanceClassifier(model_dir=str(MODEL_DIR))

# Store processed documents in memory (use database in production)
processed_documents = {}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        spacy_model="en_core_web_sm" if nlp else None,
        model_trained=classifier.trained
    )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    threshold: float = Form(0.5)
):
    """
    Upload and process a document.
    
    Args:
        file: Document file (PDF, DOCX, or TXT)
        threshold: Relevance threshold (0.0 to 1.0)
        
    Returns:
        UploadResponse with document ID and status
    """
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, DOCX, or TXT files."
            )
        
        # Generate document ID
        doc_id = generate_document_id(file.filename)
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing document: {file.filename} (ID: {doc_id})")
        
        # Process document
        start_time = time.time()
        result = process_document(str(file_path), doc_id, file.filename, threshold)
        processing_time = time.time() - start_time
        
        result['processing_time'] = processing_time
        
        # Store result
        processed_documents[doc_id] = result
        
        logger.info(f"Processed {result['total_sections']} sections in {processing_time:.2f}s")
        
        return UploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="success",
            message=f"Processed {result['total_sections']} sections, {result['relevant_sections']} relevant"
        )
    
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}", response_model=DocumentResult)
async def get_document_result(document_id: str, threshold: Optional[float] = None):
    """
    Get processing results for a document.
    
    Args:
        document_id: Document ID
        threshold: Optional threshold to refilter results
        
    Returns:
        DocumentResult with sections and metadata
    """
    if document_id not in processed_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = processed_documents[document_id]
    
    # Refilter sections if threshold provided
    if threshold is not None:
        filtered_sections = [
            s for s in result['sections'] 
            if s.relevance_score >= threshold
        ]
        result['sections'] = filtered_sections
        result['relevant_sections'] = len(filtered_sections)
        result['threshold'] = threshold
    
    return DocumentResult(**result)


@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback for a section to improve the model.
    
    Args:
        feedback: FeedbackRequest with section relevance
        
    Returns:
        FeedbackResponse with status
    """
    try:
        if feedback.document_id not in processed_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = processed_documents[feedback.document_id]
        section = next(
            (s for s in doc['sections'] if s.id == feedback.section_id),
            None
        )
        
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # Add feedback to classifier
        classifier.add_feedback(section.features, feedback.is_relevant)
        
        logger.info(
            f"Feedback received for doc {feedback.document_id}, "
            f"section {feedback.section_id}: {feedback.is_relevant}"
        )
        
        return FeedbackResponse(
            status="success",
            message="Feedback recorded successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch")
async def batch_upload(
    files: List[UploadFile] = File(...),
    threshold: float = Form(0.5)
):
    """
    Upload and process multiple documents.
    
    Args:
        files: List of document files
        threshold: Relevance threshold
        
    Returns:
        Batch upload response with document IDs
    """
    try:
        document_ids = []
        
        for file in files:
            if not validate_file_type(file.filename):
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            # Generate document ID
            doc_id = generate_document_id(file.filename)
            
            # Save uploaded file
            file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process document
            try:
                result = process_document(str(file_path), doc_id, file.filename, threshold)
                processed_documents[doc_id] = result
                document_ids.append(doc_id)
                logger.info(f"Processed: {file.filename}")
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
        
        return {
            "document_ids": document_ids,
            "total_documents": len(document_ids),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Batch upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export")
async def export_results(request: ExportRequest):
    """
    Export document results in specified format.
    
    Args:
        request: ExportRequest with document ID and format
        
    Returns:
        File download
    """
    if request.document_id not in processed_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = processed_documents[request.document_id]
    
    # Filter by threshold
    relevant_sections = [
        s for s in result['sections']
        if s.relevance_score >= request.threshold
    ]
    
    # Export based on format
    export_path = UPLOAD_DIR / f"{request.document_id}_export.{request.format}"
    
    if request.format == 'json':
        import json
        export_data = {
            'document_name': result['document_name'],
            'total_sections': result['total_sections'],
            'relevant_sections': len(relevant_sections),
            'threshold': request.threshold,
            'sections': [
                {
                    'id': s.id,
                    'title': s.title,
                    'content': s.content,
                    'relevance_score': s.relevance_score,
                    'page_number': s.page_number,
                    'tags': s.tags
                }
                for s in relevant_sections
            ]
        }
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    elif request.format == 'txt':
        lines = [
            f"Document: {result['document_name']}",
            f"Total Sections: {result['total_sections']}",
            f"Relevant Sections: {len(relevant_sections)}",
            f"Threshold: {request.threshold}",
            "\n" + "="*80 + "\n"
        ]
        
        for s in relevant_sections:
            lines.extend([
                f"\n{s.title} (Score: {s.relevance_score:.2f}, Page: {s.page_number})",
                "-" * 80,
                s.content,
                "\n"
            ])
        
        with open(export_path, 'w') as f:
            f.write('\n'.join(lines))
    
    return FileResponse(
        export_path,
        filename=f"{result['document_name']}_sections.{request.format}",
        media_type='application/octet-stream'
    )


def process_document(file_path: str, doc_id: str, filename: str, threshold: float) -> dict:
    """
    Process a document through the pipeline.
    
    Args:
        file_path: Path to document file
        doc_id: Document ID
        filename: Original filename
        threshold: Relevance threshold
        
    Returns:
        Processing result dictionary
    """
    # Parse document
    parsed = parser.parse(file_path)
    
    # Segment into sections
    sections = segmenter.segment(parsed['text'], parsed.get('pages'))
    
    # Extract features and score each section
    processed_sections = []
    relevant_count = 0
    
    for section in sections:
        # Extract features
        features = feature_extractor.extract_features(section)
        
        # Score relevance
        relevance_score = classifier.score_section(features)
        
        # Get feature tags
        tags = feature_extractor.get_feature_tags(features)
        
        # Create Section object
        section_obj = Section(
            id=section['id'],
            title=section['title'],
            content=section['content'],
            relevance_score=relevance_score,
            page_number=section.get('page_number'),
            features=features,
            tags=tags
        )
        
        processed_sections.append(section_obj)
        
        if relevance_score >= threshold:
            relevant_count += 1
    
    return {
        'document_id': doc_id,
        'document_name': filename,
        'total_sections': len(processed_sections),
        'relevant_sections': relevant_count,
        'sections': processed_sections,
        'threshold': threshold,
        'processing_time': 0.0  # Will be set by caller
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
