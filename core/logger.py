"""
Logger for AI Builder
Handles logging and history tracking
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from .config_manager import config


class HistoryLogger:
    def __init__(self):
        self.setup_logging()
        self.history_file = None  # Will be set when directory is created
        # Don't create log directory immediately, wait for output setup
    
    def setup_logging(self):
        """Setup basic logging configuration"""
        log_level = getattr(logging, config.output.log_level.upper(), logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        logging.getLogger().handlers.clear()
        
        # Create basic console handler
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        self.logger = logging.getLogger(__name__)
        self.history_file = os.path.join(config.get_output_path(), "logs", "history.jsonl")
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if self.history_file:
            log_dir = os.path.dirname(self.history_file)
            os.makedirs(log_dir, exist_ok=True)
        else:
            # Fallback - create logs directory in current output path
            log_dir = os.path.join(config.get_output_path(), "logs")
            os.makedirs(log_dir, exist_ok=True)
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.history_file)
        os.makedirs(log_dir, exist_ok=True)
    
    def add_file_handler(self):
        """Add file handler after log directory is created"""
        try:
            # Ensure we have a logger instance
            if not hasattr(self, 'logger'):
                return
                
            log_file_path = os.path.join(config.get_output_path(), "logs", "app.log")
            
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            # Check if file handler already exists
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler) and handler.baseFilename == os.path.abspath(log_file_path):
                    return  # File handler already exists
            
            # Add file handler
            file_handler = logging.FileHandler(log_file_path, mode='a')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # If we can't add file handler, continue with console logging only
            if hasattr(self, 'logger'):
                self.logger.warning(f"Could not add file handler: {str(e)}")
            else:
                print(f"Warning: Could not add file handler: {str(e)}")
    
    def log_history(self, state: str, files: List[str], version: str, metadata: Dict[str, Any] = None):
        """Log build history to JSONL file"""
        # Set history file path if not set
        if not self.history_file:
            self.history_file = os.path.join(config.get_output_path(), "logs", "history.jsonl")
            self._ensure_log_directory()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "files": files,
            "version": version,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Logged history for state: {state}")
        except Exception as e:
            self.logger.warning(f"Could not write to history file: {str(e)}")
    
    def log_llm_call(self, provider: str, model: str, prompt_length: int, response_length: int):
        """Log LLM API calls"""
        self.logger.info(
            f"LLM Call - Provider: {provider}, Model: {model}, "
            f"Prompt: {prompt_length} chars, Response: {response_length} chars"
        )
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all history entries"""
        if not self.history_file:
            self.history_file = os.path.join(config.get_output_path(), "logs", "history.jsonl")
        
        if not os.path.exists(self.history_file):
            return []
        
        history = []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        history.append(json.loads(line))
        except Exception as e:
            self.logger.warning(f"Could not read history file: {str(e)}")
        
        return history


# Global logger instance
logger = HistoryLogger()
