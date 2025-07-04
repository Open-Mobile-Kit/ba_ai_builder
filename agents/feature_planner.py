"""
Feature Planner Agent for AI Builder
Plans and prioritizes features based on analysis and architecture
"""

import os
from typing import Dict, Any, List
from core.llm_manager import llm_manager
from core.prompt_manager import prompt_manager
from core.logger import logger
from core.config_manager import config


class FeaturePlannerAgent:
    def __init__(self):
        self.name = "FeaturePlanner"
        self.description = "Plans features and creates implementation roadmap"
    
    def plan_features(self, analysis: Dict[str, Any], architecture: Dict[str, Any], detailed_features: bool = False, output_dir: str = None) -> Dict[str, Any]:
        """
        Plan features based on analysis and architecture
        
        Args:
            analysis: Project analysis from AnalyzerAgent
            architecture: Architecture design from ArchitectAgent
            detailed_features: Whether to generate detailed feature specifications
            output_dir: Output directory for detailed features (required if detailed_features=True)
            
        Returns:
            Feature plan with prioritized features and roadmap
        """
        try:
            logger.logger.info("Starting feature planning")
            
            # Prepare prompt with analysis and architecture
            prompt = prompt_manager.get_prompt(
                "features",
                analysis=analysis.get('analysis_content', ''),
                architecture=architecture.get('architecture_content', '')
            )
            
            # Generate feature plan using LLM
            features_content = llm_manager.complete(
                prompt=prompt,
                system_prompt="You are a product manager. Create a comprehensive feature plan with clear priorities."
            )
            
            # Structure the feature plan
            features_result = {
                "base_analysis": analysis,
                "base_architecture": architecture,
                "features_content": features_content,
                "metadata": {
                    "agent": self.name,
                    "version": config.output.current_version,
                    "inputs": ["analysis", "architecture"]
                },
                "feature_categories": self._extract_feature_categories(features_content),
                "timeline": self._extract_timeline(features_content)
            }

            # Generate detailed features if requested
            if detailed_features and output_dir:
                logger.logger.info("Generating detailed feature specifications...")
                detailed_specs = self.generate_detailed_features(features_result, output_dir)
                features_result["detailed_features"] = detailed_specs

            logger.logger.info("Feature planning completed")
            return features_result
            
        except Exception as e:
            logger.log_error(e, "Planning features")
            return {
                "error": str(e),
                "base_analysis": analysis,
                "base_architecture": architecture,
                "features_content": "",
                "metadata": {"agent": self.name, "error": True}
            }
    
    def _extract_feature_categories(self, content: str) -> Dict[str, List[str]]:
        """Extract categorized features from content"""
        categories = {
            "core": [],
            "enhanced": [],
            "optional": []
        }
        
        current_category = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detect category headers
            if any(keyword in line.lower() for keyword in ['core', 'must-have', 'essential']):
                current_category = "core"
            elif any(keyword in line.lower() for keyword in ['enhanced', 'should-have', 'important']):
                current_category = "enhanced"
            elif any(keyword in line.lower() for keyword in ['optional', 'nice-to-have', 'future']):
                current_category = "optional"
            
            # Extract features (lines starting with - or numbers)
            if current_category and (line.startswith('-') or line.startswith(tuple('123456789'))):
                feature = line.lstrip('-').lstrip('0123456789').lstrip('.').strip()
                if feature and len(feature) < 100:
                    categories[current_category].append(feature)
        
        return categories
    
    def _extract_timeline(self, content: str) -> Dict[str, str]:
        """Extract timeline information from content"""
        timeline = {}
        
        # Look for timeline keywords
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['phase', 'sprint', 'week', 'month', 'quarter']):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        timeline[parts[0].strip()] = parts[1].strip()
        
        return timeline
    
    def save_feature_plan(self, features: Dict[str, Any], output_dir: str) -> str:
        """Save feature plan to file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "feature_list.md")
            
            # Format content for saving
            content = f"""# Feature Plan

## Feature Overview
{features.get('features_content', 'N/A')}

## Feature Categories

### Core Features (Must-Have)
{chr(10).join(f"- {feature}" for feature in features.get('feature_categories', {}).get('core', []))}

### Enhanced Features (Should-Have)
{chr(10).join(f"- {feature}" for feature in features.get('feature_categories', {}).get('enhanced', []))}

### Optional Features (Nice-to-Have)
{chr(10).join(f"- {feature}" for feature in features.get('feature_categories', {}).get('optional', []))}

## Implementation Timeline
{chr(10).join(f"**{phase}**: {desc}" for phase, desc in features.get('timeline', {}).items())}

## Metadata
- Agent: {features.get('metadata', {}).get('agent', 'Unknown')}
- Version: {features.get('metadata', {}).get('version', 'Unknown')}
- Based on: {', '.join(features.get('metadata', {}).get('inputs', []))}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.logger.info(f"Feature plan saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving feature plan to: {output_dir}")
            raise
    

    def generate_detailed_features(self, features: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate detailed specifications for each feature using the LLM and save them to files.
        Args:
            features: The feature plan dictionary (output of plan_features)
            output_dir: Directory to save detailed feature specs
        Returns:
            Dictionary with detailed feature outputs and file paths
        """
        try:
            logger.logger.info("Generating detailed feature specifications for each feature...")
            detail_prompt_template = prompt_manager.get_prompt("feature_detail")
            detailed_features = {}
            categories = features.get('feature_categories', {})
            all_features = []
            for cat in ['core', 'enhanced', 'optional']:
                all_features.extend(categories.get(cat, []))
            logger.logger.info(f"Total features to detail: {len(all_features)}")
            os.makedirs(os.path.join(output_dir, "features"), exist_ok=True)
            for feature in all_features:
                prompt = detail_prompt_template.format(feature=feature)
                detail_content = llm_manager.complete(
                    prompt=prompt,
                    system_prompt="You are a senior product manager. Write a detailed, clear, and actionable feature specification."
                )
                safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in feature.lower()).strip('_')[:50]
                file_path = os.path.join(output_dir, "features", f"{safe_name}.md")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(detail_content)
                detailed_features[feature] = {
                    "content": detail_content,
                    "file_path": file_path
                }
                logger.logger.info(f"Detailed spec for feature '{feature}' saved to: {file_path}")
            logger.logger.info("All detailed feature specifications generated.")
            return detailed_features
        except Exception as e:
            logger.log_error(e, "Generating detailed feature specifications")
            return {"error": str(e)}

        """Save detailed feature specifications to a summary file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "detailed_features_summary.md")
            
            # Format content for saving
            content = "# Detailed Feature Specifications\n\n"
            for feature, detail in detailed_features.items():
                content += f"## {feature}\n\n"
                content += f"{detail.get('content', 'No details available')}\n\n"
                content += f"**File Path:** {detail.get('file_path', 'N/A')}\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.logger.info(f"Detailed features summary saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.log_error(e, f"Saving detailed features to: {output_dir}")
            raise


    def refine_features(self, features: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine feature plan based on feedback"""
        try:
            logger.logger.info("Refining feature plan based on feedback")
            refinement_prompt = f"""
Original Feature Plan:
{features.get('features_content', '')}

Feedback:
{feedback}

Please refine the feature plan based on the feedback provided. Adjust priorities and add/remove features as needed.
"""
            refined_content = llm_manager.complete(
                prompt=refinement_prompt,
                system_prompt="You are refining a feature plan based on feedback. Balance user needs with technical constraints."
            )
            # Update feature plan
            refined_features = features.copy()
            refined_features['features_content'] = refined_content
            refined_features['metadata']['refined'] = True
            refined_features['metadata']['feedback'] = feedback
            refined_features['feature_categories'] = self._extract_feature_categories(refined_content)
            refined_features['timeline'] = self._extract_timeline(refined_content)
            logger.logger.info("Feature plan refinement completed")
            return refined_features
        except Exception as e:
            logger.log_error(e, "Refining feature plan")
            return features


# Create feature planner instance
feature_planner = FeaturePlannerAgent()