"""
Feature extraction module for analyzing text sections.
"""
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from text sections for classification."""
    
    def __init__(self, nlp=None):
        """
        Initialize feature extractor.
        
        Args:
            nlp: Optional spaCy NLP model for entity recognition
        """
        self.nlp = nlp
        
        # Patterns for feature detection
        self.currency_pattern = re.compile(r'[$£€¥₹]\s*\d+|(\d+\.\d{2})')
        self.percentage_pattern = re.compile(r'\d+\.?\d*\s*%')
        self.date_pattern = re.compile(
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|'
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'
        )
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        
        # Table indicators
        self.table_indicators = ['|', '┃', '─', '═', '│']
        
        # List indicators
        self.bullet_pattern = re.compile(r'^\s*[•\-\*◦▪]\s+', re.MULTILINE)
        self.numbered_list_pattern = re.compile(r'^\s*\d+[\.)]\s+', re.MULTILINE)
    
    def extract_features(self, section: Dict) -> Dict:
        """
        Extract features from a section.
        
        Args:
            section: Section dictionary with 'content' key
            
        Returns:
            Dictionary of extracted features
        """
        content = section.get('content', '')
        
        features = {
            # Basic metrics
            'word_count': self._count_words(content),
            'sentence_count': self._count_sentences(content),
            'char_count': len(content),
            'line_count': len(content.split('\n')),
            
            # Numerical features
            'digit_count': sum(c.isdigit() for c in content),
            'digit_ratio': sum(c.isdigit() for c in content) / max(len(content), 1),
            'currency_count': len(self.currency_pattern.findall(content)),
            'percentage_count': len(self.percentage_pattern.findall(content)),
            'number_count': len(re.findall(r'\d+\.?\d*', content)),
            
            # Date and time
            'date_count': len(self.date_pattern.findall(content)),
            
            # Contact info
            'email_count': len(self.email_pattern.findall(content)),
            'url_count': len(self.url_pattern.findall(content)),
            'phone_count': len(self.phone_pattern.findall(content)),
            
            # Structural features
            'has_table': any(indicator in content for indicator in self.table_indicators),
            'bullet_list_count': len(self.bullet_pattern.findall(content)),
            'numbered_list_count': len(self.numbered_list_pattern.findall(content)),
            
            # Text density
            'text_density': self._calculate_text_density(content),
            
            # Position features
            'position': section.get('id', 0),
            'page_number': section.get('page_number', 1),
        }
        
        # Named entity features (if spaCy is available)
        if self.nlp:
            entity_features = self._extract_entities(content)
            features.update(entity_features)
        else:
            # Default entity features
            features.update({
                'entity_count': 0,
                'person_count': 0,
                'org_count': 0,
                'location_count': 0,
                'money_count': 0,
                'date_entity_count': 0,
            })
        
        # Derived features
        features['avg_word_length'] = features['char_count'] / max(features['word_count'], 1)
        features['avg_sentence_length'] = features['word_count'] / max(features['sentence_count'], 1)
        
        return features
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(re.findall(r'\b\w+\b', text))
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _calculate_text_density(self, text: str) -> float:
        """Calculate ratio of alphanumeric characters to total characters."""
        if not text:
            return 0.0
        alphanumeric = sum(c.isalnum() for c in text)
        return alphanumeric / len(text)
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy."""
        doc = self.nlp(text[:1000000])  # Limit text length for performance
        
        entities = {
            'PERSON': 0,
            'ORG': 0,
            'GPE': 0,  # Geopolitical entity (location)
            'MONEY': 0,
            'DATE': 0,
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_] += 1
        
        return {
            'entity_count': len(doc.ents),
            'person_count': entities['PERSON'],
            'org_count': entities['ORG'],
            'location_count': entities['GPE'],
            'money_count': entities['MONEY'],
            'date_entity_count': entities['DATE'],
        }
    
    def get_feature_tags(self, features: Dict) -> List[str]:
        """Generate human-readable tags from features."""
        tags = []
        
        if features.get('number_count', 0) > 5:
            tags.append('numbers')
        
        if features.get('has_table', False):
            tags.append('table')
        
        if features.get('date_count', 0) > 0 or features.get('date_entity_count', 0) > 0:
            tags.append('dates')
        
        if features.get('currency_count', 0) > 0 or features.get('money_count', 0) > 0:
            tags.append('financial')
        
        if features.get('bullet_list_count', 0) > 0 or features.get('numbered_list_count', 0) > 0:
            tags.append('list')
        
        if features.get('person_count', 0) > 0 or features.get('org_count', 0) > 0:
            tags.append('entities')
        
        if features.get('email_count', 0) > 0 or features.get('phone_count', 0) > 0:
            tags.append('contact_info')
        
        return tags
