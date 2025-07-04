"""
Document Writer Agent for AI Builder
Generates business and technical documents (BRD, SRS, etc.)
"""

import os
from typing import Dict, Any, List
from core.llm_manager import llm_manager
from core.prompt_manager import prompt_manager
from core.logger import logger
from core.config_manager import config


class DocumentWriterAgent:
    def __init__(self):
        self.name = "DocumentWriter"
        self.description = "Generates comprehensive business and technical documents"
        self.supported_documents = ["brd", "srs", "technical_spec", "user_guide"]
    
    def generate_brd(self, analysis: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Business Requirements Document (BRD)
        
        Args:
            analysis: Project analysis from AnalyzerAgent
            features: Feature plan from FeaturePlannerAgent
            
        Returns:
            BRD document structure
        """
        try:
            logger.logger.info("Generating Business Requirements Document (BRD)")
            
            # Prepare prompt for BRD generation
            prompt = prompt_manager.get_prompt(
                "brd",
                analysis=analysis.get('analysis_content', ''),
                features=features.get('features_content', '')
            )
            
            # Generate BRD using LLM
            brd_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are a business analyst creating a formal Business Requirements Document. Be comprehensive and professional."
            )
            
            # Structure the BRD
            brd_result = {
                "document_type": "brd",
                "content": brd_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "inputs": ["analysis", "features"],
                    "document_version": "1.0"
                },
                "sections": self._extract_document_sections(brd_content),
                "requirements": self._extract_requirements(brd_content)
            }
            
            logger.logger.info("BRD generation completed")
            return brd_result
            
        except Exception as e:
            logger.log_error(e, "Generating BRD")
            return {
                "error": str(e),
                "document_type": "brd",
                "content": "",
                "metadata": {"agent": self.name, "error": True}
            }
    
    def generate_srs(self, analysis: Dict[str, Any], architecture: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Software Requirements Specification (SRS)
        
        Args:
            analysis: Project analysis from AnalyzerAgent
            architecture: Architecture design from ArchitectAgent
            features: Feature plan from FeaturePlannerAgent
            
        Returns:
            SRS document structure
        """
        try:
            logger.logger.info("Generating Software Requirements Specification (SRS)")
            
            # Prepare prompt for SRS generation
            prompt = prompt_manager.get_prompt(
                "srs",
                analysis=analysis.get('analysis_content', ''),
                architecture=architecture.get('architecture_content', ''),
                features=features.get('features_content', '')
            )
            
            # Generate SRS using LLM
            srs_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are a technical writer creating a detailed Software Requirements Specification. Include technical details and specifications."
            )
            
            # Structure the SRS
            srs_result = {
                "document_type": "srs",
                "content": srs_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "inputs": ["analysis", "architecture", "features"],
                    "document_version": "1.0"
                },
                "sections": self._extract_document_sections(srs_content),
                "technical_requirements": self._extract_technical_requirements(srs_content)
            }
            
            logger.logger.info("SRS generation completed")
            return srs_result
            
        except Exception as e:
            logger.log_error(e, "Generating SRS")
            return {
                "error": str(e),
                "document_type": "srs",
                "content": "",
                "metadata": {"agent": self.name, "error": True}
            }
    
    def _extract_document_sections(self, content: str) -> Dict[str, str]:
        """Extract structured sections from document content"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip().lstrip('#').strip()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_requirements(self, content: str) -> List[str]:
        """Extract business requirements from BRD content"""
        requirements = []
        lines = content.split('\n')
        
        in_requirements_section = False
        for line in lines:
            line = line.strip()
            
            # Check if we're in a requirements section
            if any(keyword in line.lower() for keyword in ['requirement', 'functional', 'business rule']):
                in_requirements_section = True
                continue
            
            # Extract requirements (typically numbered or bulleted)
            if in_requirements_section and (line.startswith('-') or line.startswith(tuple('123456789'))):
                req = line.lstrip('-').lstrip('0123456789').lstrip('.').strip()
                if req and len(req) > 10:  # Filter out short/empty requirements
                    requirements.append(req)
            
            # Stop if we hit a new major section
            if line.startswith('#') and in_requirements_section:
                in_requirements_section = False
        
        return requirements
    
    def _extract_technical_requirements(self, content: str) -> List[str]:
        """Extract technical requirements from SRS content"""
        tech_requirements = []
        lines = content.split('\n')
        
        in_tech_section = False
        for line in lines:
            line = line.strip()
            
            # Check if we're in a technical requirements section
            if any(keyword in line.lower() for keyword in ['technical', 'system', 'performance', 'security']):
                in_tech_section = True
                continue
            
            # Extract technical requirements
            if in_tech_section and (line.startswith('-') or line.startswith(tuple('123456789'))):
                req = line.lstrip('-').lstrip('0123456789').lstrip('.').strip()
                if req and len(req) > 10:
                    tech_requirements.append(req)
            
            # Stop if we hit a new major section
            if line.startswith('#') and in_tech_section:
                in_tech_section = False
        
        return tech_requirements
    
    def save_document(self, document: Dict[str, Any], output_dir: str) -> str:
        """Save document to file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            doc_type = document.get('document_type', 'document')
            file_path = os.path.join(output_dir, f"{doc_type}.md")
            
            # Format content for saving
            content = f"""# {doc_type.upper()} - {config.project.name}

{document.get('content', 'N/A')}

---

## Document Metadata
- Document Type: {doc_type.upper()}
- Version: {document.get('metadata', {}).get('document_version', '1.0')}
- Generated by: {document.get('metadata', {}).get('agent', 'Unknown')}
- Based on: {', '.join(document.get('metadata', {}).get('inputs', []))}
- Project Version: {document.get('metadata', {}).get('version', 'Unknown')}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.logger.info(f"{doc_type.upper()} saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving {doc_type} to: {output_dir}")
            raise
    
    def refine_document(self, document: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine document based on feedback"""
        try:
            doc_type = document.get('document_type', 'document')
            logger.logger.info(f"Refining {doc_type} based on feedback")
            
            refinement_prompt = f"""
Original {doc_type.upper()}:
{document.get('content', '')}

Feedback:
{feedback}

Please refine the {doc_type.upper()} based on the feedback provided. Maintain professional formatting and completeness.
"""
            
            refined_content = llm_manager.complete(
                prompt=refinement_prompt,
                system_prompt=f"You are refining a {doc_type.upper()} based on feedback. Maintain document structure and professionalism."
            )
            
            # Update document
            refined_document = document.copy()
            refined_document['content'] = refined_content
            refined_document['metadata']['refined'] = True
            refined_document['metadata']['feedback'] = feedback
            refined_document['sections'] = self._extract_document_sections(refined_content)
            
            # Update requirements based on document type
            if doc_type == 'brd':
                refined_document['requirements'] = self._extract_requirements(refined_content)
            elif doc_type == 'srs':
                refined_document['technical_requirements'] = self._extract_technical_requirements(refined_content)
            
            logger.logger.info(f"{doc_type.upper()} refinement completed")
            return refined_document
            
        except Exception as e:
            logger.log_error(e, f"Refining {doc_type}")
            return document


# Create document writer instance
document_writer = DocumentWriterAgent()