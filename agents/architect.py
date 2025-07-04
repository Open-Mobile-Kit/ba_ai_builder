"""
Architect Agent for AI Builder
Designs system architecture based on project analysis
"""

import os
from typing import Dict, Any, List
from core.llm_manager import llm_manager
from core.prompt_manager import prompt_manager
from core.logger import logger
from core.config_manager import config


class ArchitectAgent:
    def __init__(self):
        self.name = "Architect"
        self.description = "Designs system architecture and technical specifications"
    
    def design_architecture(self, analysis: Dict[str, Any], requirements: str = "") -> Dict[str, Any]:
        """
        Design system architecture based on project analysis
        
        Args:
            analysis: Project analysis from AnalyzerAgent
            requirements: Additional technical requirements
            
        Returns:
            Architecture design with components, technology stack, etc.
        """
        try:
            logger.logger.info("Starting architecture design")
            
            # Prepare prompt with analysis
            prompt = prompt_manager.get_prompt(
                "architecture",
                analysis=analysis.get('analysis_content', ''),
                requirements=requirements
            )
            
            # Generate architecture using LLM
            architecture_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are a senior software architect. Design scalable and maintainable system architecture."
            )
            
            # Structure the architecture
            architecture_result = {
                "base_analysis": analysis,
                "architecture_content": architecture_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "based_on": analysis.get('metadata', {}).get('agent', 'Unknown')
                },
                "components": self._extract_components(architecture_content),
                "technology_stack": self._extract_technology_stack(architecture_content)
            }
            
            logger.logger.info("Architecture design completed")
            return architecture_result
            
        except Exception as e:
            logger.log_error(e, "Designing architecture")
            return {
                "error": str(e),
                "base_analysis": analysis,
                "architecture_content": "",
                "metadata": {"agent": self.name, "error": True}
            }
    
    def _extract_components(self, content: str) -> List[str]:
        """Extract system components from architecture content"""
        components = []
        
        # Look for common component indicators
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['component', 'service', 'module', 'layer']):
                if line and not line.startswith('#'):
                    # Extract component name
                    component = line.split(':')[0].strip()
                    if component and len(component) < 50:
                        components.append(component)
        
        return list(set(components))  # Remove duplicates
    
    def _extract_technology_stack(self, content: str) -> Dict[str, List[str]]:
        """Extract technology stack from architecture content"""
        tech_stack = {
            "backend": [],
            "frontend": [],
            "mobile": [],
            "database": [],
            "infrastructure": []
        }
        
        content_lower = content.lower()
        
        # Backend technologies
        backend_techs = ['python', 'java', 'node.js', 'go', 'rust', 'c#', '.net']
        for tech in backend_techs:
            if tech in content_lower:
                tech_stack["backend"].append(tech)
        
        # Frontend technologies
        frontend_techs = ['react', 'vue', 'angular', 'svelte', 'html', 'css', 'javascript']
        for tech in frontend_techs:
            if tech in content_lower:
                tech_stack["frontend"].append(tech)

        # Mobile technologies
        mobile_techs = ['flutter', 'react native', 'swift', 'kotlin', 'java (android)', 'objective-c']
        for tech in mobile_techs:
            if tech in content_lower:
                tech_stack["mobile"].append(tech)


        # Database technologies
        db_techs = ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlite', 'elasticsearch']
        for tech in db_techs:
            if tech in content_lower:
                tech_stack["database"].append(tech)
        
        # Infrastructure
        infra_techs = ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'nginx', 'apache']
        for tech in infra_techs:
            if tech in content_lower:
                tech_stack["infrastructure"].append(tech)
        
        return tech_stack
    
    def save_architecture(self, architecture: Dict[str, Any], output_dir: str) -> str:
        """Save architecture to file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "system_architecture.md")
            
            # Format content for saving
            content = f"""# System Architecture Design

## Architecture Overview
{architecture.get('architecture_content', 'N/A')}

## System Components
{chr(10).join(f"- {comp}" for comp in architecture.get('components', []))}

## Technology Stack

### Backend
{chr(10).join(f"- {tech}" for tech in architecture.get('technology_stack', {}).get('backend', []))}

### Frontend
{chr(10).join(f"- {tech}" for tech in architecture.get('technology_stack', {}).get('frontend', []))}

### Mobile
{chr(10).join(f"- {tech}" for tech in architecture.get('technology_stack', {}).get('mobile', []))}

### Database
{chr(10).join(f"- {tech}" for tech in architecture.get('technology_stack', {}).get('database', []))}

### Infrastructure
{chr(10).join(f"- {tech}" for tech in architecture.get('technology_stack', {}).get('infrastructure', []))}

## Metadata
- Agent: {architecture.get('metadata', {}).get('agent', 'Unknown')}
- Version: {architecture.get('metadata', {}).get('version', 'Unknown')}
- Based on: {architecture.get('metadata', {}).get('based_on', 'Unknown')}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.logger.info(f"Architecture saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving architecture to: {output_dir}")
            raise
    
    def refine_architecture(self, architecture: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine architecture based on feedback"""
        try:
            logger.logger.info("Refining architecture based on feedback")
            
            refinement_prompt = f"""
Original Architecture:
{architecture.get('architecture_content', '')}

Feedback:
{feedback}

Please refine the architecture design based on the feedback provided. Address the concerns while maintaining system integrity.
"""
            
            refined_content = llm_manager.complete(
                prompt=refinement_prompt,
                system_prompt="You are refining a system architecture based on feedback. Ensure technical feasibility."
            )
            
            # Update architecture
            refined_architecture = architecture.copy()
            refined_architecture['architecture_content'] = refined_content
            refined_architecture['metadata']['refined'] = True
            refined_architecture['metadata']['feedback'] = feedback
            refined_architecture['components'] = self._extract_components(refined_content)
            refined_architecture['technology_stack'] = self._extract_technology_stack(refined_content)
            
            logger.logger.info("Architecture refinement completed")
            return refined_architecture
            
        except Exception as e:
            logger.log_error(e, "Refining architecture")
            return architecture


# Create architect instance
architect = ArchitectAgent()