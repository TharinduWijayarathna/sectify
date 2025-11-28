"""
Tests for relevance classifier module.
"""
import pytest
from relevance_classifier import RelevanceClassifier


def test_classifier_initialization():
    """Test classifier initializes correctly."""
    classifier = RelevanceClassifier()
    assert classifier.trained == False


def test_heuristic_scoring():
    """Test heuristic scoring works."""
    classifier = RelevanceClassifier()
    
    # Section with data indicators
    features = {
        'word_count': 150,
        'digit_count': 20,
        'digit_ratio': 0.1,
        'number_count': 10,
        'has_table': True,
        'entity_count': 5,
        'text_density': 0.75,
        'currency_count': 3,
        'date_count': 2,
    }
    
    score = classifier.score_section(features)
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should score high with these features


def test_low_score_for_minimal_features():
    """Test that sections with minimal features score low."""
    classifier = RelevanceClassifier()
    
    # Minimal features
    features = {
        'word_count': 10,
        'digit_count': 0,
        'digit_ratio': 0.0,
        'number_count': 0,
        'has_table': False,
        'entity_count': 0,
        'text_density': 0.3,
    }
    
    score = classifier.score_section(features)
    assert score < 0.5  # Should score low


# Note: Add tests for ML training once test data is available
