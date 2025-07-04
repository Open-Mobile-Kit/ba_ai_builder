# BA AI Builder 🎯

**Automated Business Analysis and Documentation Generation System**

AI Builder is an AI-powered system for automatically generating business and technical analysis documents, using multiple coordinated agents to create BRD, SRS, and professional project documentation.

## 🚀 Key Features

- **Multi-Agent Architecture**: Specialized agents (Analyzer, Architect, Feature Planner, Document Writer, Refiner, Validator)
- **Multi-LLM Support**: Supports multiple providers (OpenAI, Ollama, Anthropic, Gemini)
- **Flexible Configuration**: Easily configurable via YAML files
- **Vector Storage**: Document storage and retrieval using ChromaDB
- **Automated Validation**: Automatic quality and format checks
- **Iterative Refinement**: Document improvement based on feedback
- **Comprehensive Logging**: Tracks the entire build process

## 🏗️ Project Structure

```
ai_builder/
├── agents/                 # AI agents
│   ├── analyzer.py        # Requirement analysis
│   ├── architect.py       # System architecture design
│   ├── feature_planner.py # Feature planning
│   ├── document_writer.py # Document generation
│   ├── refiner.py         # Content refinement
│   ├── validator.py       # Quality validation
│   └── vector_manager.py  # Vector store management
│
├── core/                  # Core modules
│   ├── llm_manager.py     # LLM provider management
│   ├── prompt_manager.py  # Prompt management
│   ├── config_manager.py  # Configuration management
│   └── logger.py          # Logging system
│
├── orchestrator.py        # Agent orchestration
├── main.py               # Main entry point
├── config.yaml           # System configuration
├── requirements.txt      # Dependencies
│
├── prompts/              # Template prompts
│   ├── analysis.txt
│   ├── architecture.txt
│   ├── features.txt
│   ├── brd.txt
│   └── srs.txt
│
├── templates/            # Document templates
│   ├── brd_template.md
│   └── srs_template.md
│
├── output/v1/           # Output directory
│   ├── analysis/
│   ├── architecture/
│   ├── features/
│   ├── documents/
│   ├── validation/
│   ├── report/
│   └── logs/
│
└── vector_store/        # ChromaDB storage
```

## ⚙️ Installation and Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
or
python setup.py
```

### 2. Configure the System

Edit the `config.yaml` file:

```yaml
llm:
    provider: ollama  # or openai, anthropic, gemini
    model_name: llama3
    temperature: 0.2
    max_tokens: 4000
    api_key: ""  # For OpenAI, Anthropic, etc.
    base_url: "http://localhost:11434"  # For Ollama

vector_store:
    type: chromadb
    persist_directory: "./vector_store"
    collection_name: "ai_builder_docs"

output:
    base_path: "./output"
    current_version: "v1"
    log_level: "INFO"
```

### 3. Run AI Builder

```bash
# Option 1: Directly pass requirements
python main.py "Build an online sales management system with features: product management, order management, customer management, payment"

# Option 2: From a file
python main.py requirements.txt

# Option 3: With additional context
python main.py "Build e-commerce system" --context '{"budget": "100k", "timeline": "6 months"}'

# Option 4: With a different version
python main.py requirements.txt --version v2

# Option 5: With a custom output directory
python main.py requirements.txt --output-dir /path/to/custom/output

# Option 6: Combine options
python main.py requirements.txt --output-dir ./projects/ecommerce --version v1.1 --context context.json
```

### 4. Refine with Feedback

```bash
python main.py requirements.txt --refine documents --feedback "Add more details about security requirements"
```

## 📁 Custom Output Directories

AI Builder allows you to customize the output directory for better project organization:

### Command Line Usage
```bash
# Use an absolute directory
python main.py requirements.txt --output-dir /Users/username/Documents/projects/my-project

# Use a relative directory
python main.py requirements.txt --output-dir ./projects/ecommerce

# Short form
python main.py requirements.txt -o ./output/ecommerce-v2
```

### Programmatic Usage
```python
from core.config_manager import config
from orchestrator import orchestrator

# Set custom output directory
config.output.base_path = "/path/to/custom/output"
orchestrator.refresh_output_paths()

# Run build
result = orchestrator.build_project(requirements)
```

### Output Structure
With a custom output directory, the structure will be created as follows:
```
/custom/output/path/v1/
├── analysis/
├── architecture/
├── features/
├── documents/
├── validation/
├── report/
└── logs/
```

## 📊 Output Structure

The system generates a standard output structure:

```
output/v1/
├── analysis/
│   └── analysis_overview.md       # Overview of analysis
├── architecture/
│   └── system_architecture.md     # System architecture design
├── features/
│   ├── features/
│   └── feature_list.md           # Feature list
├── documents/
│   ├── brd.md                    # Business Requirements Document
│   └── srs.md                    # Software Requirements Specification
├── validation/
│   └── validation_report.json    # Validation report
├── report/
│   └── final_report.md          # Final summary report
└── logs/
        ├── history.jsonl            # Build history
        └── app.log                  # Application logs
```

## 🔄 Workflow

1. **Analysis**: Analyze requirements and identify stakeholders
2. **Architecture**: Design system architecture and technology stack
3. **Feature Planning**: Plan features and prioritize
4. **Document Generation**: Generate BRD, SRS, and technical documents
5. **Validation**: Check quality and format
6. **Final Report**: Create a summary report

## 🤖 Agents

### AnalyzerAgent
- Analyze project requirements
- Identify stakeholders and objectives
- Assess risks and constraints

### ArchitectAgent
- Design system architecture
- Recommend technology stack
- Define components and interfaces

### FeaturePlannerAgent
- Plan features
- Prioritize and create a roadmap
- Define user stories and acceptance criteria

### DocumentWriterAgent
- Generate BRD and SRS
- Professional technical documentation
- Structured standard format

### RefinerAgent
- Improve content based on feedback
- Iterative refinement
- Quality enhancement

### ValidatorAgent
- Check format and structure
- Quality scoring
- Compliance checking

## 🔧 LLM Providers

### Ollama (Local)
```yaml
llm:
    provider: ollama
    model_name: llama3
    base_url: "http://localhost:11434"
```

### OpenAI
```yaml
llm:
    provider: openai
    model_name: gpt-4
    api_key: "your-api-key"
```

### Anthropic Claude
```yaml
llm:
    provider: anthropic
    model_name: claude-3-sonnet-20240229
    api_key: "your-api-key"
```

### Google Gemini
```yaml
llm:
    provider: gemini
    model_name: gemini-pro
    api_key: "your-api-key"
```

## 📝 Customization

### Custom Prompts
Edit prompts in the `prompts/` directory:
- `analysis.txt`: Prompt for analysis
- `architecture.txt`: Prompt for architecture design
- `features.txt`: Prompt for feature planning
- `brd.txt`: Prompt for BRD generation
- `srs.txt`: Prompt for SRS generation

### Custom Templates
Edit templates in the `templates/` directory:
- `brd_template.md`: Template for BRD
- `srs_template.md`: Template for SRS

## 🚀 Extensibility

### Add a New Agent
1. Create an agent file in `agents/`
2. Implement the required methods
3. Import and use it in `orchestrator.py`

### Add a New LLM Provider
1. Add logic in `llm_manager.py`
2. Update the configuration schema
3. Test with the new provider

### Add a New Document Type
1. Add a prompt template
2. Update `document_writer.py`
3. Add validation rules

## 📋 Requirements

- Python >= 3.9
- ChromaDB
- Jinja2
- PyYAML
- Pydantic
- LLM provider packages (ollama, openai, anthropic, google-generativeai)

## 🔍 Troubleshooting

### LLM Connection Issues
- Check API keys
- Verify network connectivity
- Check provider status

### Vector Store Issues
- Ensure ChromaDB directory is writable
- Check disk space
- Verify ChromaDB installation

### Validation Errors
- Check output file permissions
- Verify markdown format
- Review validation rules

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**AI Builder** - Automate analysis and documentation for your projects! 🎯

