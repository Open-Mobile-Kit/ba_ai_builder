#!/usr/bin/env python3
"""
Setup script for AI Builder
Helps with initial configuration and dependency checking
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is >= 3.9"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = [
        "output",
        "vector_store",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    return True


def check_llm_providers():
    """Check which LLM providers are available"""
    print("🤖 Checking LLM providers...")
    
    providers = {
        "ollama": {"package": "ollama", "description": "Local LLM (Ollama)"},
        "openai": {"package": "openai", "description": "OpenAI GPT models"},
        "anthropic": {"package": "anthropic", "description": "Anthropic Claude"},
        "google-generativeai": {"package": "google.generativeai", "description": "Google Gemini"}
    }
    
    available_providers = []
    
    for provider, info in providers.items():
        try:
            __import__(info["package"])
            print(f"   ✅ {info['description']}")
            available_providers.append(provider)
        except ImportError:
            print(f"   ❌ {info['description']} (not installed)")
    
    if not available_providers:
        print("⚠️  No LLM providers available. Please install at least one.")
        return False
    
    return available_providers


def create_sample_config():
    """Create a sample configuration file if it doesn't exist"""
    config_file = "config.yaml"
    
    if os.path.exists(config_file):
        print(f"✅ Configuration file already exists: {config_file}")
        return True
    
    print(f"📝 Creating sample configuration: {config_file}")
    
    sample_config = """# AI Builder Configuration
llm:
  provider: ollama  # Options: ollama, openai, anthropic, gemini
  model_name: llama3
  temperature: 0.2
  max_tokens: 4000
  api_key: ""  # Required for OpenAI, Anthropic, Gemini
  base_url: "http://localhost:11434"  # For Ollama

vector_store:
  type: chromadb
  persist_directory: "./vector_store"
  collection_name: "ai_builder_docs"

output:
  base_path: "./output"
  current_version: "v1"
  log_level: "INFO"

project:
  name: "AI Builder Project"
  description: "Automated business analysis and documentation generation"
  author: "AI Builder System"
"""
    
    with open(config_file, 'w') as f:
        f.write(sample_config)
    
    print(f"✅ Sample configuration created: {config_file}")
    print("📝 Please edit the configuration file with your LLM provider settings")
    return True


def test_basic_functionality():
    """Test basic system functionality"""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test imports
        from core.config_manager import config
        from core.logger import logger
        print("   ✅ Core modules import successfully")
        
        # Test configuration loading
        print(f"   ✅ Configuration loaded: {config.llm.provider}")
        
        # Test directory structure
        output_path = config.get_output_path()
        print(f"   ✅ Output path: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False


def main():
    """Main setup function"""
    print("🎯 AI Builder Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Please install dependencies manually: pip install -r requirements.txt")
    
    # Setup directories
    setup_directories()
    
    # Check LLM providers
    available_providers = check_llm_providers()
    
    # Create sample config
    create_sample_config()
    
    # Test basic functionality
    if test_basic_functionality():
        print("\\n🎉 Setup completed successfully!")
        print("\\n🚀 Next steps:")
        print("1. Edit config.yaml with your LLM provider settings")
        print("2. Run: python main.py 'Your project requirements'")
        print("3. Or run: python example.py for a demo")
        
        if available_providers:
            print(f"\\n💡 Available providers: {', '.join(available_providers)}")
        
    else:
        print("\\n❌ Setup completed with errors")
        print("Please check the error messages above and try again")


if __name__ == "__main__":
    main()
