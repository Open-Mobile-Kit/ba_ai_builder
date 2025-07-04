"""
Analyzer Agent for AI Builder
Performs initial project analysis and requirement gathering
"""
from core.llm_manager import llm_manager
from core.prompt_manager import prompt_manager
from core.logger import logger
from core.config_manager import config
import os
from typing import Dict, Any



class AnalyzerAgent:
    def __init__(self):
        self.name = "Analyzer"
        self.description = "Analyzes project requirements and provides comprehensive analysis"
    
    def analyze_requirements(self, requirements: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze project requirements and generate comprehensive analysis
        
        Args:
            requirements: Raw project requirements
            context: Additional context information
            
        Returns:
            Analysis results containing overview, stakeholders, technical requirements, etc.
        """
        try:
            logger.logger.info("Starting requirements analysis")
            
            # Prepare prompt with requirements
            prompt = prompt_manager.get_prompt(
                "analysis",
                requirements=requirements,
                context=context or {}
            )
            
            # Generate analysis using LLM
            analysis_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are an expert business analyst. Provide thorough and structured analysis."
            )
            
            # Structure the analysis
            analysis_result = {
                "raw_requirements": requirements,
                "analysis_content": analysis_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "context": context
                },
                "sections": self._extract_sections(analysis_content)
            }
            
            logger.logger.info("Requirements analysis completed")
            return analysis_result
            
        except Exception as e:
            logger.log_error(e, "Analyzing requirements")
            return {
                "error": str(e),
                "raw_requirements": requirements,
                "analysis_content": "",
                "metadata": {"agent": self.name, "error": True}
            }
    
    def analyze_bnmp(self, bnm: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze business needs and market position
        
        Args:
            bnm: Business needs and market position description
            context: Additional context information
            
        Returns:
            Analysis results containing business needs, market analysis, etc.
        """
        try:
            logger.logger.info("Starting business needs and market position analysis")
            
            # Prepare prompt with business needs
            prompt = prompt_manager.get_prompt(
                "bnm_analysis",
                bnm=bnm,
                context=context or {}
            )
            
            # Generate analysis using LLM
            analysis_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are a business strategist. Analyze the business needs and market position."
            )
            
            # Structure the analysis
            analysis_result = {
                "business_needs": bnm,
                "analysis_content": analysis_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "context": context
                },
                "sections": self._extract_sections(analysis_content)
            }
            
            logger.logger.info("Business needs and market position analysis completed")
            return analysis_result
            
        except Exception as e:
            logger.log_error(e, "Analyzing business needs and market position")
            return {
                "error": str(e),
                "business_needs": bnm,
                "analysis_content": "",
                "metadata": {"agent": self.name, "error": True}
            }

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract structured sections from analysis content"""
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
    
    def save_analysis(self, analysis: Dict[str, Any], output_dir: str) -> str:
        """Save analysis to file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "analysis_overview.md")
            
            # Format content for saving
            content = f"""# Project Analysis Overview

## Raw Requirements
{analysis.get('raw_requirements', 'N/A')}

## Analysis Content
{analysis.get('analysis_content', 'N/A')}

## Metadata
- Agent: {analysis.get('metadata', {}).get('agent', 'Unknown')}
- Version: {analysis.get('metadata', {}).get('version', 'Unknown')}
- Generated: {analysis.get('metadata', {}).get('timestamp', 'Unknown')}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.logger.info(f"Analysis saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving analysis to: {output_dir}")
            raise
    
    def refine_analysis(self, analysis: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine analysis based on feedback"""
        try:
            logger.logger.info("Refining analysis based on feedback")
            
            refinement_prompt = f"""
Original Analysis:
{analysis.get('analysis_content', '')}

Feedback:
{feedback}

Please refine the analysis based on the feedback provided. Keep the good parts and improve the areas mentioned in the feedback.
"""
            
            refined_content = llm_manager.complete(
                prompt=refinement_prompt,
                system_prompt="You are refining a business analysis based on feedback. Maintain structure while addressing concerns."
            )
            
            # Update analysis
            refined_analysis = analysis.copy()
            refined_analysis['analysis_content'] = refined_content
            refined_analysis['metadata']['refined'] = True
            refined_analysis['metadata']['feedback'] = feedback
            refined_analysis['sections'] = self._extract_sections(refined_content)
            
            logger.logger.info("Analysis refinement completed")
            return refined_analysis
            
        except Exception as e:
            logger.log_error(e, "Refining analysis")
            return analysis


# Create analyzer instance
analyzer = AnalyzerAgent()
