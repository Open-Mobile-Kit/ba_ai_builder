"""
Refiner Agent for AI Builder
Refines and improves generated documents based on feedback
"""

import os
from typing import Dict, Any, List
from core.llm_manager import llm_manager
from core.prompt_manager import prompt_manager
from core.logger import logger
from core.config_manager import config


class RefinerAgent:
    def __init__(self):
        self.name = "Refiner"
        self.description = "Refines and improves generated content based on feedback"
        self.refinement_strategies = [
            "content_enhancement",
            "structure_improvement",
            "clarity_optimization",
            "completeness_check"
        ]
    
    def refine_content(self, content: str, feedback: str, content_type: str = "document") -> Dict[str, Any]:
        """
        Refine content based on feedback
        
        Args:
            content: Original content to refine
            feedback: Feedback for improvement
            content_type: Type of content (document, analysis, architecture, etc.)
            
        Returns:
            Refined content with improvements
        """
        try:
            logger.logger.info(f"Refining {content_type} based on feedback")
            
            # Analyze feedback to determine refinement strategy
            refinement_strategy = self._analyze_feedback(feedback)
            
            # Prepare refinement prompt
            prompt = self._create_refinement_prompt(content, feedback, content_type, refinement_strategy)
            
            # Generate refined content
            refined_content = llm_manager.complete(
                prompt=prompt,
                system_prompt=f"You are an expert editor refining {content_type}. Focus on addressing feedback while maintaining quality."
            )
            
            # Structure the refinement result
            refinement_result = {
                "original_content": content,
                "refined_content": refined_content,
                "feedback": feedback,
                "content_type": content_type,
                "refinement_strategy": refinement_strategy,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "refinement_round": 1
                },
                "improvements": self._identify_improvements(content, refined_content)
            }
            
            logger.logger.info(f"{content_type.capitalize()} refinement completed")
            return refinement_result
            
        except Exception as e:
            logger.log_error(e, f"Refining {content_type}")
            return {
                "error": str(e),
                "original_content": content,
                "refined_content": content,
                "feedback": feedback,
                "metadata": {"agent": self.name, "error": True}
            }
    
    def _analyze_feedback(self, feedback: str) -> str:
        """Analyze feedback to determine appropriate refinement strategy"""
        feedback_lower = feedback.lower()
        
        if any(keyword in feedback_lower for keyword in ['structure', 'organize', 'format', 'section']):
            return "structure_improvement"
        elif any(keyword in feedback_lower for keyword in ['unclear', 'confusing', 'explain', 'clarify']):
            return "clarity_optimization"
        elif any(keyword in feedback_lower for keyword in ['missing', 'incomplete', 'add', 'include']):
            return "completeness_check"
        else:
            return "content_enhancement"
    
    def _create_refinement_prompt(self, content: str, feedback: str, content_type: str, strategy: str) -> str:
        """Create appropriate refinement prompt based on strategy"""
        base_prompt = f"""
Original {content_type}:
{content}

Feedback received:
{feedback}

Refinement strategy: {strategy}
"""
        
        strategy_instructions = {
            "structure_improvement": "Focus on improving the structure, organization, and formatting. Reorganize sections for better flow.",
            "clarity_optimization": "Focus on making the content clearer and easier to understand. Simplify complex concepts.",
            "completeness_check": "Focus on adding missing information and ensuring comprehensive coverage of all topics.",
            "content_enhancement": "Focus on overall content quality, accuracy, and professional presentation."
        }
        
        instruction = strategy_instructions.get(strategy, strategy_instructions["content_enhancement"])
        
        return f"""{base_prompt}

{instruction}

Please provide the refined {content_type} that addresses the feedback while maintaining or improving the overall quality.
"""
    
    def _identify_improvements(self, original: str, refined: str) -> List[str]:
        """Identify improvements made during refinement"""
        improvements = []
        
        # Basic comparison metrics
        original_lines = len(original.split('\n'))
        refined_lines = len(refined.split('\n'))
        
        if refined_lines > original_lines:
            improvements.append(f"Expanded content from {original_lines} to {refined_lines} lines")
        
        # Check for new sections (headers)
        original_headers = [line for line in original.split('\n') if line.strip().startswith('#')]
        refined_headers = [line for line in refined.split('\n') if line.strip().startswith('#')]
        
        if len(refined_headers) > len(original_headers):
            improvements.append(f"Added {len(refined_headers) - len(original_headers)} new sections")
        
        # Check for structural improvements
        if '##' in refined and '##' not in original:
            improvements.append("Improved document structure with sub-sections")
        
        # Check for lists and organization
        original_lists = original.count('- ')
        refined_lists = refined.count('- ')
        
        if refined_lists > original_lists:
            improvements.append(f"Added {refined_lists - original_lists} new list items for better organization")
        
        return improvements
    
    def iterative_refinement(self, content: str, feedback_list: List[str], content_type: str = "document") -> Dict[str, Any]:
        """
        Perform iterative refinement based on multiple feedback rounds
        
        Args:
            content: Original content
            feedback_list: List of feedback from different rounds
            content_type: Type of content being refined
            
        Returns:
            Final refined content after all iterations
        """
        try:
            logger.logger.info(f"Starting iterative refinement for {content_type}")
            
            current_content = content
            refinement_history = []
            
            for i, feedback in enumerate(feedback_list, 1):
                logger.logger.info(f"Refinement round {i}")
                
                # Refine content based on current feedback
                refinement_result = self.refine_content(current_content, feedback, content_type)
                
                # Update current content for next iteration
                current_content = refinement_result.get('refined_content', current_content)
                
                # Track refinement history
                refinement_history.append({
                    "round": i,
                    "feedback": feedback,
                    "strategy": refinement_result.get('refinement_strategy'),
                    "improvements": refinement_result.get('improvements', [])
                })
            
            # Final result
            final_result = {
                "original_content": content,
                "final_refined_content": current_content,
                "total_rounds": len(feedback_list),
                "refinement_history": refinement_history,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "content_type": content_type,
                    "iterative": True
                }
            }
            
            logger.logger.info(f"Iterative refinement completed after {len(feedback_list)} rounds")
            return final_result
            
        except Exception as e:
            logger.log_error(e, f"Iterative refinement for {content_type}")
            return {
                "error": str(e),
                "original_content": content,
                "final_refined_content": content,
                "metadata": {"agent": self.name, "error": True}
            }
    
    def save_refinement(self, refinement: Dict[str, Any], output_dir: str, filename: str = None) -> str:
        """Save refinement result to file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            if not filename:
                content_type = refinement.get('content_type', 'document')
                filename = f"refined_{content_type}.md"
            
            file_path = os.path.join(output_dir, filename)
            
            # Determine content to save
            if 'final_refined_content' in refinement:
                # Iterative refinement
                content_to_save = refinement['final_refined_content']
                refinement_info = f"""
## Refinement Summary
- Total refinement rounds: {refinement.get('total_rounds', 0)}
- Content type: {refinement.get('metadata', {}).get('content_type', 'Unknown')}
- Agent: {refinement.get('metadata', {}).get('agent', 'Unknown')}

### Refinement History
{chr(10).join([f"**Round {r['round']}**: {r['feedback']} (Strategy: {r['strategy']})" for r in refinement.get('refinement_history', [])])}
"""
            else:
                # Single refinement
                content_to_save = refinement.get('refined_content', '')
                refinement_info = f"""
## Refinement Summary
- Strategy: {refinement.get('refinement_strategy', 'Unknown')}
- Improvements: {', '.join(refinement.get('improvements', []))}
- Agent: {refinement.get('metadata', {}).get('agent', 'Unknown')}
"""
            
            # Format final content
            full_content = f"""{content_to_save}

---
{refinement_info}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.logger.info(f"Refinement saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving refinement to: {output_dir}")
            raise


# Create refiner instance
refiner = RefinerAgent()