#!/usr/bin/env python3
"""
AI Builder - Main Entry Point
Automated business analysis and documentation generation system
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import orchestrator
from core.config_manager import config
from core.logger import logger


def main():
    """Main entry point for AI Builder"""
    parser = argparse.ArgumentParser(
        description="AI Builder - Automated business analysis and documentation generation"
    )
    
    parser.add_argument(
        "requirements",
        help="Project requirements (string or path to file)"
    )
    
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    
    parser.add_argument(
        "--context",
        help="Additional context information (JSON string or path to file)"
    )
    
    parser.add_argument(
        "--version",
        default="v1",
        help="Output version (default: v1)"
    )
    
    parser.add_argument(
        "--output-dir",
        "--output",
        "-o",
        help="Custom output directory (default: ./output)"
    )
    
    parser.add_argument(
        "--feedback",
        help="Feedback for refinement (string or path to file)"
    )

    parser.add_argument(
        "--refine",
        choices=["documents", "analysis", "architecture", "features"],
        help="Refine specific component with feedback"
    )

    parser.add_argument(
        "--detailed-features",
        action="store_true",
        help="Generate detailed feature specifications for each feature (optional, default: off)"
    )
    
    args = parser.parse_args()
    
    try:
        # Update configuration if needed
        if args.version != "v1":
            config.output.current_version = args.version
        
        # Update output directory if provided
        if args.output_dir:
            # Validate output directory
            is_valid, result = validate_output_directory(args.output_dir)
            if not is_valid:
                print(f"❌ Error: Cannot use output directory '{args.output_dir}': {result}")
                sys.exit(1)
            
            # Update configuration
            config.output.base_path = result
            # Refresh orchestrator output paths (this creates the directory structure)
            orchestrator.refresh_output_paths()
            # Add file handler to logger now that directory exists
            logger.add_file_handler()
            logger.logger.info(f"Using custom output directory: {result}")
        else:
            # Ensure default output structure exists
            orchestrator._setup_output_structure()
            # Add file handler to logger now that directory exists
            logger.add_file_handler()
        
        # Load requirements
        requirements = load_text_input(args.requirements)
        
        # Load context if provided
        context = {}
        if args.context:
            import json
            context_text = load_text_input(args.context)
            try:
                context = json.loads(context_text)
            except json.JSONDecodeError:
                context = {"additional_info": context_text}
        
        logger.logger.info("Starting AI Builder")
        logger.logger.info(f"Requirements: {requirements[:100]}...")
        logger.logger.info(f"Version: {args.version}")
        logger.logger.info(f"LLM Provider: {config.llm.provider}")
        logger.logger.info(f"Model: {config.llm.model_name}")
        
        if args.refine and args.feedback:
            # Refinement mode
            feedback = load_text_input(args.feedback)
            result = orchestrator.refine_with_feedback(feedback, args.refine)
            print(f"Refinement completed: {result['status']}")
        else:
            # Full build mode
            result = orchestrator.build_project(requirements, context, generate_detailed_features=args.detailed_features)

            print("\n" + "="*60)
            print("AI BUILDER - BUILD COMPLETED")
            print("="*60)
            print(f"Version: {result['version']}")
            print(f"Duration: {result.get('duration', 0):.2f} seconds")
            print(f"Output directory: {config.get_output_path()}")

            # Print build summary
            print("\nBuild Summary:")
            for state_name, state_result in result['states'].items():
                status = state_result.get('status', 'unknown')
                file_count = len(state_result.get('files', []))
                print(f"  {state_name.capitalize()}: {status} ({file_count} files)")

            # Print generated files
            all_files = []
            for state_result in result['states'].values():
                all_files.extend(state_result.get('files', []))

            print(f"\nGenerated Files ({len(all_files)}):")
            for file_path in all_files:
                print(f"  - {file_path}")

            if args.detailed_features:
                features_state = result['states'].get('features', {})
                detailed_features = features_state.get('detailed_features', {})
                print(f"\nDetailed feature specifications generated: {len(detailed_features)}")
                for feature, detail in detailed_features.items():
                    print(f"  - {feature}: {detail.get('file_path', '')}")

            print("\n" + "="*60)
        
    except Exception as e:
        logger.log_error(e, "Main execution")
        print(f"Error: {str(e)}")
        sys.exit(1)


def load_text_input(input_str):
    """Load text from string or file path"""
    if Path(input_str).exists():
        with open(input_str, 'r', encoding='utf-8') as f:
            return f.read()
    return input_str


def validate_output_directory(output_dir):
    """Validate that output directory is writable"""
    try:
        output_path = Path(output_dir).resolve()
        
        # Create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = output_path / ".ai_builder_test"
        test_file.write_text("test")
        test_file.unlink()
        
        return True, str(output_path)
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    main()
