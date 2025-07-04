"""
Validator Agent for AI Builder
Validates generated documents and checks format compliance
"""

import os
import re
from typing import Dict, List, Any, Tuple
from core.config_manager import config
from core.logger import logger


class ValidatorAgent:
    def __init__(self):
        self.validation_rules = {
            'markdown': {
                'required_headers': ['#', '##', '###'],
                'required_sections': [],
                'max_line_length': 120
            },
            'brd': {
                'required_sections': [
                    'Executive Summary',
                    'Business Objectives',
                    'Functional Requirements',
                    'Non-functional Requirements'
                ]
            },
            'srs': {
                'required_sections': [
                    'System Overview',
                    'Functional Specifications',
                    'Technical Requirements',
                    'Interface Requirements'
                ]
            }
        }
    
    def validate_document(self, content: str, doc_type: str = 'markdown') -> Dict[str, Any]:
        """
        Validate document content and format
        
        Args:
            content: Document content to validate
            doc_type: Type of document (markdown, brd, srs)
            
        Returns:
            Validation result with errors and warnings
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'score': 0,
            'suggestions': []
        }
        
        try:
            # Check basic format
            self._check_basic_format(content, validation_result)
            
            # Check markdown structure
            if doc_type in ['markdown', 'brd', 'srs']:
                self._check_markdown_structure(content, validation_result)
            
            # Check specific document requirements
            if doc_type in ['brd', 'srs']:
                self._check_document_sections(content, doc_type, validation_result)
            
            # Calculate overall score
            validation_result['score'] = self._calculate_score(validation_result)
            validation_result['valid'] = validation_result['score'] >= 70
            
            logger.logger.info(f"Validated {doc_type} document - Score: {validation_result['score']}")
            
        except Exception as e:
            logger.log_error(e, f"Validating {doc_type} document")
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_result
    
    def _check_basic_format(self, content: str, result: Dict[str, Any]):
        """Check basic document format"""
        if not content.strip():
            result['errors'].append("Document is empty")
            return
        
        lines = content.split('\n')
        
        # Check for extremely long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 200:
                result['warnings'].append(f"Line {i} is very long ({len(line)} characters)")
        
        # Check for basic structure
        if len(lines) < 5:
            result['warnings'].append("Document seems too short")
    
    def _check_markdown_structure(self, content: str, result: Dict[str, Any]):
        """Check markdown structure and formatting"""
        lines = content.split('\n')
        
        has_headers = False
        header_levels = []
        
        for line in lines:
            # Check for headers
            if line.strip().startswith('#'):
                has_headers = True
                level = len(line) - len(line.lstrip('#'))
                header_levels.append(level)
        
        if not has_headers:
            result['errors'].append("No markdown headers found")
        
        # Check header hierarchy
        if header_levels:
            for i in range(1, len(header_levels)):
                if header_levels[i] > header_levels[i-1] + 1:
                    result['warnings'].append("Header level skipped - poor hierarchy")
                    break
    
    def _check_document_sections(self, content: str, doc_type: str, result: Dict[str, Any]):
        """Check for required document sections"""
        if doc_type not in self.validation_rules:
            return
        
        required_sections = self.validation_rules[doc_type].get('required_sections', [])
        content_lower = content.lower()
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in content_lower:
                missing_sections.append(section)
        
        if missing_sections:
            result['errors'].extend([f"Missing required section: {section}" for section in missing_sections])
    
    def _calculate_score(self, result: Dict[str, Any]) -> int:
        """Calculate validation score (0-100)"""
        base_score = 100
        
        # Deduct points for errors and warnings
        error_penalty = len(result['errors']) * 20
        warning_penalty = len(result['warnings']) * 5
        
        score = max(0, base_score - error_penalty - warning_penalty)
        return score
    
    def validate_file(self, file_path: str, doc_type: str = 'markdown') -> Dict[str, Any]:
        """Validate a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.validate_document(content, doc_type)
            result['file_path'] = file_path
            
            return result
            
        except Exception as e:
            logger.log_error(e, f"Validating file: {file_path}")
            return {
                'valid': False,
                'errors': [f"Failed to read file: {str(e)}"],
                'warnings': [],
                'score': 0,
                'file_path': file_path
            }
    
    def validate_project_output(self, output_dir: str) -> Dict[str, Any]:
        """Validate all files in project output directory"""
        validation_results = {
            'overall_valid': True,
            'files': {},
            'summary': {
                'total_files': 0,
                'valid_files': 0,
                'average_score': 0
            }
        }
        
        try:
            if not os.path.exists(output_dir):
                validation_results['overall_valid'] = False
                return validation_results
            
            # Find all markdown files
            md_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md'):
                        md_files.append(os.path.join(root, file))
            
            total_score = 0
            valid_count = 0
            
            for file_path in md_files:
                # Determine document type from filename
                filename = os.path.basename(file_path).lower()
                doc_type = 'markdown'
                if 'brd' in filename:
                    doc_type = 'brd'
                elif 'srs' in filename:
                    doc_type = 'srs'
                
                result = self.validate_file(file_path, doc_type)
                validation_results['files'][file_path] = result
                
                total_score += result['score']
                if result['valid']:
                    valid_count += 1
            
            validation_results['summary']['total_files'] = len(md_files)
            validation_results['summary']['valid_files'] = valid_count
            validation_results['summary']['average_score'] = total_score / len(md_files) if md_files else 0
            validation_results['overall_valid'] = valid_count == len(md_files)
            
            logger.logger.info(f"Validated project output - {valid_count}/{len(md_files)} files valid")
            
        except Exception as e:
            logger.log_error(e, f"Validating project output: {output_dir}")
            validation_results['overall_valid'] = False
        
        return validation_results


# Create validator instance
validator = ValidatorAgent()
