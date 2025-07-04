"""
Orchestrator for AI Builder
Coordinates all agents and manages the build process
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.config_manager import config
from core.logger import logger
from agents.analyzer import analyzer
from agents.architect import architect
from agents.feature_planner import feature_planner
from agents.document_writer import document_writer
from agents.refiner import refiner
from agents.validator import validator
from agents.vector_manager import vector_manager


class AIBuilderOrchestrator:
    def __init__(self):
        self.version = config.output.current_version
        self.output_base = config.get_output_path()
        self.state_dirs = {
            1: "state_1_analysis",
            2: "state_2_architecture", 
            3: "state_3_features",
            4: "state_4_documents",
            5: "state_5_validation",
            6: "state_6_final"
        }
        self.build_state = {}
        self._setup_output_structure()
    
    def _setup_output_structure(self):
        """Create output directory structure"""
        try:
            # Create base output directory
            os.makedirs(self.output_base, exist_ok=True)
            
            # Create state directories
            for state_dir in self.state_dirs.values():
                os.makedirs(os.path.join(self.output_base, state_dir), exist_ok=True)
            
            # Create logs directory
            os.makedirs(os.path.join(self.output_base, "logs"), exist_ok=True)
            
            logger.logger.info(f"Output structure created at: {self.output_base}")
            
        except Exception as e:
            logger.log_error(e, f"Setting up output structure at {self.output_base}")
            raise
    
    def build_project(self, requirements: str, context: Dict[str, Any] = None, generate_detailed_features: bool = False) -> Dict[str, Any]:
        """
        Main build process - orchestrates all agents
        
        Args:
            requirements: Project requirements
            context: Additional context information
            
        Returns:
            Build result with all generated artifacts
        """
        try:
            logger.logger.info("Starting AI Builder project build")
            
            build_result = {
                "start_time": datetime.now(),
                "requirements": requirements,
                "context": context or {},
                "states": {},
                "files": [],
                "version": self.version
            }
            
            # State 1: Analysis
            build_result["states"]["analysis"] = self._run_analysis(requirements, context)
            
            # State 2: Architecture Design
            build_result["states"]["architecture"] = self._run_architecture(
                build_result["states"]["analysis"]
            )
            
            # State 3: Feature Planning
            build_result["states"]["features"] = self._run_feature_planning(
                build_result["states"]["analysis"],
                build_result["states"]["architecture"],
                generate_detailed_features=generate_detailed_features
            )
            
            # State 4: Document Generation
            build_result["states"]["documents"] = self._run_document_generation(
                build_result["states"]["analysis"],
                build_result["states"]["architecture"],
                build_result["states"]["features"]
            )
            
            # State 5: Validation
            build_result["states"]["validation"] = self._run_validation()
            
            # State 6: Final Report
            build_result["states"]["final"] = self._generate_final_report(build_result)
            
            build_result["end_time"] = datetime.now()
            build_result["duration"] = (build_result["end_time"] - build_result["start_time"]).total_seconds()
            
            # Log final history
            logger.log_history(
                state="build_complete",
                files=build_result["files"],
                version=self.version,
                metadata={"duration": build_result["duration"]}
            )
            
            logger.logger.info(f"Project build completed in {build_result['duration']:.2f} seconds")
            return build_result
            
        except Exception as e:
            logger.log_error(e, "Project build")
            raise
    
    def _run_analysis(self, requirements: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis phase"""
        try:
            logger.logger.info("Running State 1: Analysis")
            
            # Analyze requirements
            analysis_result = analyzer.analyze_requirements(requirements, context)

            # Analyze business needs and market position
            # If context is provided, use it; otherwise, create an empty context

            if context.get("business_needs") is not None and context.get("market_context") is not None:
                bnm_result = analyzer.analyze_bnmp(
                    bnm=context["business_needs"],
                    context=context["market_context"]
                )

            
            # Save analysis
            output_dir = os.path.join(self.output_base, self.state_dirs[1])
            analysis_file = analyzer.save_analysis(analysis_result, output_dir)
            
            # Store in vector database
            vector_manager.add_document(
                content=analysis_result.get('analysis_content', ''),
                metadata={
                    "type": "analysis",
                    "agent": "analyzer",
                    "version": self.version,
                    "file_path": analysis_file
                }
            )
            
            # Log history
            logger.log_history(
                state="analysis_complete",
                files=[analysis_file],
                version=self.version,
                metadata={"agent": "analyzer"}
            )
            
            return {
                "result": analysis_result,
                "files": [analysis_file],
                "status": "completed"
            }
            
        except Exception as e:
            logger.log_error(e, "Analysis phase")
            return {"status": "failed", "error": str(e)}
    
    def _run_architecture(self, analysis_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run architecture design phase"""
        try:
            logger.logger.info("Running State 2: Architecture Design")
            
            analysis_result = analysis_state.get("result", {})
            
            # Design architecture
            architecture_result = architect.design_architecture(analysis_result)
            
            # Save architecture
            output_dir = os.path.join(self.output_base, self.state_dirs[2])
            architecture_file = architect.save_architecture(architecture_result, output_dir)
            
            # Store in vector database
            vector_manager.add_document(
                content=architecture_result.get('architecture_content', ''),
                metadata={
                    "type": "architecture",
                    "agent": "architect",
                    "version": self.version,
                    "file_path": architecture_file
                }
            )
            
            # Log history
            logger.log_history(
                state="architecture_complete",
                files=[architecture_file],
                version=self.version,
                metadata={"agent": "architect"}
            )
            
            return {
                "result": architecture_result,
                "files": [architecture_file],
                "status": "completed"
            }
            
        except Exception as e:
            logger.log_error(e, "Architecture phase")
            return {"status": "failed", "error": str(e)}
    
    def _run_feature_planning(self, analysis_state: Dict[str, Any], architecture_state: Dict[str, Any], generate_detailed_features: bool = False) -> Dict[str, Any]:
        """Run feature planning phase. Optionally generate detailed feature specs."""
        try:
            logger.logger.info("Running State 3: Feature Planning")
            analysis_result = analysis_state.get("result", {})
            architecture_result = architecture_state.get("result", {})
            # Plan features
            output_dir = os.path.join(self.output_base, self.state_dirs[3])
            features_result = feature_planner.plan_features(analysis_result, architecture_result, 
                                                         detailed_features=True, 
                                                         output_dir=output_dir)
            # Save features
            features_file = feature_planner.save_feature_plan(features_result, output_dir)
            
            # Get detailed features if they were generated
            detailed_features = features_result.get("detailed_features", {})
            detailed_files = [v["file_path"] for v in detailed_features.values() if isinstance(v, dict) and "file_path" in v]
            
            # Add each detailed feature spec to vector db if generated
            for feature, detail in detailed_features.items():
                if isinstance(detail, dict) and "content" in detail and "file_path" in detail:
                    vector_manager.add_document(
                        content=detail["content"],
                        metadata={
                            "type": "feature_detail",
                            "agent": "feature_planner",
                            "feature": feature,
                            "version": self.version,
                            "file_path": detail["file_path"]
                        }
                    )
                
            # Store in vector database
            vector_manager.add_document(
                content=features_result.get('features_content', ''),
                metadata={
                    "type": "features",
                    "agent": "feature_planner",
                    "version": self.version,
                    "file_path": features_file
                }
            )
            # Log history
            logger.log_history(
                state="features_complete",
                files=[features_file] + detailed_files,
                version=self.version,
                metadata={"agent": "feature_planner", "detailed_features": list(detailed_features.keys()) if detailed_features else None}
            )
            return {
                "result": features_result,
                "files": [features_file] + detailed_files,
                "detailed_features": detailed_features,
                "status": "completed"
            }
        except Exception as e:
            logger.log_error(e, "Feature planning phase")
            return {"status": "failed", "error": str(e)}
    
    def _run_document_generation(self, analysis_state: Dict[str, Any], architecture_state: Dict[str, Any], features_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run document generation phase"""
        try:
            logger.logger.info("Running State 4: Document Generation")
            
            analysis_result = analysis_state.get("result", {})
            architecture_result = architecture_state.get("result", {})
            features_result = features_state.get("result", {})
            
            output_dir = os.path.join(self.output_base, self.state_dirs[4])
            generated_files = []
            documents = {}
            
            # Generate BRD
            brd_result = document_writer.generate_brd(analysis_result, features_result)
            brd_file = document_writer.save_document(brd_result, output_dir)
            generated_files.append(brd_file)
            documents["brd"] = brd_result
            
            # Generate SRS
            srs_result = document_writer.generate_srs(analysis_result, architecture_result, features_result)
            srs_file = document_writer.save_document(srs_result, output_dir)
            generated_files.append(srs_file)
            documents["srs"] = srs_result
            
            # Store documents in vector database
            for doc_type, doc_result in documents.items():
                vector_manager.add_document(
                    content=doc_result.get('content', ''),
                    metadata={
                        "type": doc_type,
                        "agent": "document_writer",
                        "version": self.version,
                        "file_path": generated_files[-1] if doc_type == "srs" else generated_files[-2]
                    }
                )
            
            # Log history
            logger.log_history(
                state="documents_complete",
                files=generated_files,
                version=self.version,
                metadata={"agent": "document_writer", "documents": list(documents.keys())}
            )
            
            return {
                "result": documents,
                "files": generated_files,
                "status": "completed"
            }
            
        except Exception as e:
            logger.log_error(e, "Document generation phase")
            return {"status": "failed", "error": str(e)}
    
    def _run_validation(self) -> Dict[str, Any]:
        """Run validation phase"""
        try:
            logger.logger.info("Running State 5: Validation")
            
            # Validate all generated files
            validation_result = validator.validate_project_output(self.output_base)
            
            # Save validation report
            output_dir = os.path.join(self.output_base, self.state_dirs[5])
            os.makedirs(output_dir, exist_ok=True)
            
            validation_file = os.path.join(output_dir, "validation_report.json")
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_result, f, indent=2, ensure_ascii=False, default=str)
            
            # Log history
            logger.log_history(
                state="validation_complete",
                files=[validation_file],
                version=self.version,
                metadata={
                    "agent": "validator",
                    "overall_valid": validation_result.get("overall_valid", False),
                    "average_score": validation_result.get("summary", {}).get("average_score", 0)
                }
            )
            
            return {
                "result": validation_result,
                "files": [validation_file],
                "status": "completed"
            }
            
        except Exception as e:
            logger.log_error(e, "Validation phase")
            return {"status": "failed", "error": str(e)}
    
    def _generate_final_report(self, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final project report"""
        try:
            logger.logger.info("Running State 6: Final Report Generation")
            
            output_dir = os.path.join(self.output_base, self.state_dirs[6])
            os.makedirs(output_dir, exist_ok=True)
            
            # Create comprehensive final report
            report_content = f"""# {config.project.name} - Final Report

## Project Overview
**Version**: {self.version}
**Generated**: {build_result['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
**Duration**: {build_result.get('duration', 0):.2f} seconds

## Requirements
{build_result.get('requirements', 'N/A')}

## Build Summary

### Analysis Phase
- Status: {build_result['states']['analysis']['status']}
- Files: {len(build_result['states']['analysis'].get('files', []))}

### Architecture Phase
- Status: {build_result['states']['architecture']['status']}
- Files: {len(build_result['states']['architecture'].get('files', []))}

### Features Phase
- Status: {build_result['states']['features']['status']}
- Files: {len(build_result['states']['features'].get('files', []))}

### Documents Phase
- Status: {build_result['states']['documents']['status']}
- Files: {len(build_result['states']['documents'].get('files', []))}

### Validation Phase
- Status: {build_result['states']['validation']['status']}
- Overall Valid: {build_result['states']['validation'].get('result', {}).get('overall_valid', False)}

## Generated Files
{chr(10).join([f"- {file}" for state in build_result['states'].values() for file in state.get('files', [])])}

## Vector Store Statistics
{vector_manager.get_collection_stats()}

## Project Metadata
- Author: {config.project.author}
- Description: {config.project.description}
- LLM Provider: {config.llm.provider}
- Model: {config.llm.model_name}
"""
            
            report_file = os.path.join(output_dir, "final_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Log history
            logger.log_history(
                state="final_report_complete",
                files=[report_file],
                version=self.version,
                metadata={"agent": "orchestrator", "total_files": len(build_result.get('files', []))}
            )
            
            return {
                "result": {"report_content": report_content},
                "files": [report_file],
                "status": "completed"
            }
            
        except Exception as e:
            logger.log_error(e, "Final report generation")
            return {"status": "failed", "error": str(e)}
    
    def refine_with_feedback(self, feedback: str, target_state: str = "documents") -> Dict[str, Any]:
        """Refine specific build state based on feedback"""
        try:
            logger.logger.info(f"Refining {target_state} based on feedback")
            
            if target_state == "documents":
                # Refine documents
                docs_state = self.build_state.get("documents", {})
                if docs_state.get("result"):
                    for doc_type, doc_result in docs_state["result"].items():
                        refined_doc = refiner.refine_content(
                            doc_result.get("content", ""),
                            feedback,
                            doc_type
                        )
                        
                        # Save refined document
                        output_dir = os.path.join(self.output_base, self.state_dirs[4], "refined")
                        refiner.save_refinement(refined_doc, output_dir, f"refined_{doc_type}.md")
            
            return {"status": "completed", "refined_state": target_state}
            
        except Exception as e:
            logger.log_error(e, f"Refining {target_state}")
            return {"status": "failed", "error": str(e)}
    
    def refresh_output_paths(self):
        """Refresh output paths based on current configuration"""
        self.version = config.output.current_version
        self.output_base = config.get_output_path()
        self._setup_output_structure()
        logger.logger.info(f"Output paths refreshed: {self.output_base}")


# Create orchestrator instance
orchestrator = AIBuilderOrchestrator()
