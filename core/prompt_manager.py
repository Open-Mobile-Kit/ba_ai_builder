"""
Prompt Manager for AI Builder
Handles loading and formatting prompts with templates
"""

import os
from typing import Dict, Any, Optional
from jinja2 import Template, FileSystemLoader, Environment
from .config_manager import config
from .logger import logger


class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.env = Environment(loader=FileSystemLoader(prompts_dir))
        self._ensure_prompts_directory()
    
    def _ensure_prompts_directory(self):
        """Ensure prompts directory exists"""
        os.makedirs(self.prompts_dir, exist_ok=True)
    
    def get_prompt(self, name: str, **kwargs) -> str:
        """
        Load and format a prompt template
        
        Args:
            name: Prompt template name (without .txt extension)
            **kwargs: Variables to replace in template
            
        Returns:
            Formatted prompt string
        """
        try:
            template_file = f"{name}.txt"
            template_path = os.path.join(self.prompts_dir, template_file)
            
            if os.path.exists(template_path):
                template = self.env.get_template(template_file)
                return template.render(**kwargs)
            else:
                # Return default prompt if template not found
                logger.logger.warning(f"Prompt template not found: {template_file}")
                return self._get_default_prompt(name, **kwargs)
        
        except Exception as e:
            logger.log_error(e, f"Loading prompt template: {name}")
            return self._get_default_prompt(name, **kwargs)
    
    def _get_default_prompt(self, name: str, **kwargs) -> str:
        """Get default prompt if template file not found"""
        defaults = {
            "analysis": """
Analyze the following project requirements and provide a comprehensive analysis:

Requirements: {{requirements}}

Please provide:
1. Project overview and objectives
2. Key stakeholders and their needs
3. Technical requirements and constraints
4. Risk assessment
5. Success criteria
""",
            "architecture": """
Design the system architecture for the following project:

Project Analysis: {{analysis}}

Please provide:
1. High-level system architecture
2. Component breakdown
3. Technology stack recommendations
4. Integration points
5. Scalability considerations
""",
            "features": """
Create a detailed feature list based on the project analysis:

Analysis: {{analysis}}
Architecture: {{architecture}}

Please provide:
1. Core features (must-have)
2. Enhanced features (should-have)
3. Optional features (nice-to-have)
4. Feature prioritization
5. Implementation timeline
""",
            "brd": """
Create a Business Requirements Document (BRD) based on the following:

Analysis: {{analysis}}
Features: {{features}}

Please create a comprehensive BRD including:
1. Executive Summary
2. Business Objectives
3. Functional Requirements
4. Non-functional Requirements
5. Acceptance Criteria
""",
            "srs": """
Create a Software Requirements Specification (SRS) based on the following:

Analysis: {{analysis}}
Architecture: {{architecture}}
Features: {{features}}

Please create a detailed SRS including:
1. System Overview
2. Functional Specifications
3. Technical Requirements
4. Interface Requirements
5. Performance Requirements
"""
        }
        
        template_str = defaults.get(name, "Please provide detailed analysis for: {{requirements}}")
        template = Template(template_str)
        return template.render(**kwargs)
    
    def save_prompt(self, name: str, content: str):
        """Save a prompt template to file"""
        template_path = os.path.join(self.prompts_dir, f"{name}.txt")
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.logger.info(f"Saved prompt template: {name}")


# Global prompt manager instance
prompt_manager = PromptManager()
