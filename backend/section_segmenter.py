"""
Section segmentation module for splitting documents into logical sections.
"""
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class SectionSegmenter:
    """Segment documents into sections based on structure and formatting."""
    
    def __init__(self, min_section_length: int = 20):
        self.min_section_length = min_section_length
        
        # Regex patterns for section detection
        self.patterns = {
            'numbered': re.compile(r'^(\d+\.)+\s+(.+)$', re.MULTILINE),
            'roman': re.compile(r'^([IVXivx]+\.)\s+(.+)$', re.MULTILINE),
            'lettered': re.compile(r'^([A-Z]\.)\s+(.+)$', re.MULTILINE),
            'all_caps': re.compile(r'^([A-Z][A-Z\s]{3,})$', re.MULTILINE),
            'title_case': re.compile(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$', re.MULTILINE),
        }
    
    def segment(self, text: str, pages: List[Dict] = None) -> List[Dict]:
        """
        Segment text into sections.
        
        Args:
            text: Full document text
            pages: Optional page information
            
        Returns:
            List of section dictionaries
        """
        sections = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Find section boundaries
        boundaries = self._find_section_boundaries(lines)
        
        # Extract sections
        for i, (start, end, title) in enumerate(boundaries):
            content = '\n'.join(lines[start:end]).strip()
            
            if len(content) < self.min_section_length:
                continue
            
            # Determine page number if pages info is available
            page_number = self._get_page_number(start, lines, pages) if pages else None
            
            section = {
                'id': i + 1,
                'title': title or f'Section {i + 1}',
                'content': content,
                'start_line': start,
                'end_line': end,
                'page_number': page_number
            }
            
            sections.append(section)
        
        # If no sections found, create one from entire text
        if not sections and len(text.strip()) >= self.min_section_length:
            sections.append({
                'id': 1,
                'title': 'Document Content',
                'content': text.strip(),
                'start_line': 0,
                'end_line': len(lines),
                'page_number': 1
            })
        
        return sections
    
    def _find_section_boundaries(self, lines: List[str]) -> List[tuple]:
        """Find section boundaries in document."""
        boundaries = []
        current_start = 0
        current_title = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Check if line matches any header pattern
            is_header, title = self._is_section_header(stripped)
            
            if is_header and i > current_start:
                # Save previous section
                boundaries.append((current_start, i, current_title))
                current_start = i
                current_title = title
        
        # Add final section
        if current_start < len(lines):
            boundaries.append((current_start, len(lines), current_title))
        
        return boundaries
    
    def _is_section_header(self, line: str) -> tuple:
        """Check if line is a section header."""
        # Check numbered sections (1., 1.1, 1.1.1, etc.)
        match = self.patterns['numbered'].match(line)
        if match:
            return True, line
        
        # Check roman numerals
        match = self.patterns['roman'].match(line)
        if match:
            return True, line
        
        # Check lettered sections
        match = self.patterns['lettered'].match(line)
        if match:
            return True, line
        
        # Check ALL CAPS headers (at least 4 chars)
        match = self.patterns['all_caps'].match(line)
        if match and len(line.replace(' ', '')) >= 4:
            return True, line
        
        # Check Title Case headers
        match = self.patterns['title_case'].match(line)
        if match and 10 <= len(line) <= 100:
            return True, line
        
        # Check for visual breaks (multiple dashes, equals, etc.)
        if re.match(r'^[-=*]{5,}$', line):
            return True, 'Section Break'
        
        return False, None
    
    def _get_page_number(self, line_num: int, lines: List[str], pages: List[Dict]) -> int:
        """Estimate page number for a given line."""
        if not pages or len(pages) == 1:
            return 1
        
        # Calculate approximate line position
        total_lines = len(lines)
        position_ratio = line_num / total_lines if total_lines > 0 else 0
        
        # Map to page number
        page_num = int(position_ratio * len(pages)) + 1
        return min(page_num, len(pages))
