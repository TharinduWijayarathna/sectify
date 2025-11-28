"""
Tests for section segmenter module.
"""
import pytest
from section_segmenter import SectionSegmenter


def test_segmenter_initialization():
    """Test segmenter initializes correctly."""
    segmenter = SectionSegmenter(min_section_length=20)
    assert segmenter.min_section_length == 20


def test_numbered_section_detection():
    """Test detection of numbered sections."""
    segmenter = SectionSegmenter()
    
    text = """
1. Introduction
This is the first section.

2. Methodology  
This is the second section.
    """
    
    sections = segmenter.segment(text)
    assert len(sections) >= 1


def test_minimum_section_length():
    """Test that very short sections are filtered."""
    segmenter = SectionSegmenter(min_section_length=50)
    
    text = "Short text"
    
    sections = segmenter.segment(text)
    assert len(sections) == 0


# Note: Add more tests for different section patterns
