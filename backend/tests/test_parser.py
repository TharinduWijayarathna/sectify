"""
Tests for document parser module.
"""
import pytest
from pathlib import Path
from document_parser import DocumentParser


def test_parser_initialization():
    """Test parser initializes correctly."""
    parser = DocumentParser()
    assert parser.supported_formats == {'.pdf', '.docx', '.txt'}


def test_unsupported_format():
    """Test parser rejects unsupported formats."""
    parser = DocumentParser()
    with pytest.raises(ValueError):
        parser.parse('test.xlsx')


def test_file_not_found():
    """Test parser handles missing files."""
    parser = DocumentParser()
    with pytest.raises(FileNotFoundError):
        parser.parse('nonexistent.pdf')


# Note: Add more comprehensive tests with actual test documents
# These would require sample PDF/DOCX/TXT files in a test_files directory
