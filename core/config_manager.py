"""
Configuration Manager for AI Builder
Handles loading and managing configuration from config.yaml
"""

import yaml
import os
from typing import Dict, Any
from pydantic import BaseModel


class LLMConfig(BaseModel):
    provider: str
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 4000
    api_key: str = ""
    base_url: str = ""


class VectorStoreConfig(BaseModel):
    type: str = "chromadb"
    persist_directory: str = "./vector_store"
    collection_name: str = "ai_builder_docs"


class OutputConfig(BaseModel):
    base_path: str = "./output"
    current_version: str = "v1"
    log_level: str = "INFO"


class ProjectConfig(BaseModel):
    name: str = "AI Builder Project"
    description: str = ""
    author: str = "AI Builder System"


class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config_data = self._load_config()
        
        self.llm = LLMConfig(**self._config_data.get("llm", {}))
        self.vector_store = VectorStoreConfig(**self._config_data.get("vector_store", {}))
        self.output = OutputConfig(**self._config_data.get("output", {}))
        self.project = ProjectConfig(**self._config_data.get("project", {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def reload(self):
        """Reload configuration from file"""
        self._config_data = self._load_config()
        self.llm = LLMConfig(**self._config_data.get("llm", {}))
        self.vector_store = VectorStoreConfig(**self._config_data.get("vector_store", {}))
        self.output = OutputConfig(**self._config_data.get("output", {}))
        self.project = ProjectConfig(**self._config_data.get("project", {}))
    
    def get_output_path(self) -> str:
        """Get current version output path"""
        return os.path.join(self.output.base_path, self.output.current_version)


# Global config instance
config = Config()
