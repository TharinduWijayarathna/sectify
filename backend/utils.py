"""
Utility functions for the backend.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import hashlib
import time


def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_file_type(filename: str) -> bool:
    """Check if file type is supported."""
    supported_extensions = {'.pdf', '.docx', '.txt'}
    return Path(filename).suffix.lower() in supported_extensions


def generate_document_id(filename: str) -> str:
    """Generate unique document ID."""
    timestamp = str(time.time())
    content = f"{filename}{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()


def format_error_response(error: Exception) -> dict:
    """Format error as JSON response."""
    return {
        "error": type(error).__name__,
        "message": str(error)
    }


def ensure_dir(directory: str) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_spacy_model(model_name: str = "en_core_web_sm"):
    """Load spaCy model with error handling."""
    try:
        import spacy
        return spacy.load(model_name)
    except OSError:
        logging.warning(
            f"spaCy model '{model_name}' not found. "
            "Install it with: python -m spacy download en_core_web_sm"
        )
        return None
    except Exception as e:
        logging.error(f"Error loading spaCy model: {e}")
        return None
