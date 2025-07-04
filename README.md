# AI Builder 🎯

**Automated Business Analysis and Documentation Generation System**

AI Builder là một hệ thống tự động sinh tài liệu phân tích kinh doanh và kỹ thuật bằng AI, sử dụng nhiều agents phối hợp để tạo ra BRD, SRS và các tài liệu dự án chuyên nghiệp.

## 🚀 Tính năng chính

- **Multi-Agent Architecture**: Hệ thống agents chuyên biệt (Analyzer, Architect, Feature Planner, Document Writer, Refiner, Validator)
- **Multi-LLM Support**: Hỗ trợ nhiều provider (OpenAI, Ollama, Anthropic, Gemini)
- **Flexible Configuration**: Cấu hình dễ dàng qua file YAML
- **Vector Storage**: Lưu trữ và tìm kiếm tài liệu bằng ChromaDB
- **Automated Validation**: Kiểm tra chất lượng và format tự động
- **Iterative Refinement**: Cải thiện tài liệu dựa trên feedback
- **Comprehensive Logging**: Tracking toàn bộ quá trình build

## 🏗️ Cấu trúc dự án

```
ai_builder/
├── agents/                 # Các AI agents
│   ├── analyzer.py        # Phân tích yêu cầu
│   ├── architect.py       # Thiết kế kiến trúc
│   ├── feature_planner.py # Lập kế hoạch tính năng
│   ├── document_writer.py # Sinh tài liệu
│   ├── refiner.py         # Cải thiện nội dung
│   ├── validator.py       # Kiểm tra chất lượng
│   └── vector_manager.py  # Quản lý vector store
│
├── core/                  # Core modules
│   ├── llm_manager.py     # Quản lý LLM providers
│   ├── prompt_manager.py  # Quản lý prompts
│   ├── config_manager.py  # Quản lý cấu hình
│   └── logger.py          # Logging system
│
├── orchestrator.py        # Điều phối các agents
├── main.py               # Entry point chính
├── config.yaml           # Cấu hình hệ thống
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
│   ├── state_1_analysis/
│   ├── state_2_architecture/
│   ├── state_3_features/
│   ├── state_4_documents/
│   ├── state_5_validation/
│   ├── state_6_final/
│   └── logs/
│
└── vector_store/        # ChromaDB storage
```

## ⚙️ Cài đặt và sử dụng

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình hệ thống

Chỉnh sửa file `config.yaml`:

```yaml
llm:
  provider: ollama  # hoặc openai, anthropic, gemini
  model_name: llama3
  temperature: 0.2
  max_tokens: 4000
  api_key: ""  # Cho OpenAI, Anthropic, etc.
  base_url: "http://localhost:11434"  # Cho Ollama

vector_store:
  type: chromadb
  persist_directory: "./vector_store"
  collection_name: "ai_builder_docs"

output:
  base_path: "./output"
  current_version: "v1"
  log_level: "INFO"
```

### 3. Chạy AI Builder

```bash
# Cách 1: Truyền requirements trực tiếp
python main.py "Xây dựng hệ thống quản lý bán hàng online với các tính năng: quản lý sản phẩm, đơn hàng, khách hàng, thanh toán"

# Cách 2: Từ file
python main.py requirements.txt

# Cách 3: Với context bổ sung
python main.py "Build e-commerce system" --context '{"budget": "100k", "timeline": "6 months"}'

# Cách 4: Với version khác
python main.py requirements.txt --version v2

# Cách 5: Với custom output directory
python main.py requirements.txt --output-dir /path/to/custom/output

# Cách 6: Tổ hợp các options
python main.py requirements.txt --output-dir ./projects/ecommerce --version v1.1 --context context.json
```

### 4. Refine với feedback

```bash
python main.py requirements.txt --refine documents --feedback "Cần thêm chi tiết về security requirements"
```

## 📁 Custom Output Directories

AI Builder cho phép bạn tùy chỉnh thư mục output để tổ chức dự án tốt hơn:

### Command Line Usage
```bash
# Sử dụng thư mục tuyệt đối
python main.py requirements.txt --output-dir /Users/username/Documents/projects/my-project

# Sử dụng thư mục tương đối
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
Với custom output directory, cấu trúc sẽ được tạo như sau:
```
/custom/output/path/v1/
├── state_1_analysis/
├── state_2_architecture/
├── state_3_features/
├── state_4_documents/
├── state_5_validation/
├── state_6_final/
└── logs/
```

## 📊 Output Structure

Hệ thống sinh ra cấu trúc output chuẩn:

```
output/v1/
├── state_1_analysis/
│   └── analysis_overview.md       # Phân tích tổng quan
├── state_2_architecture/
│   └── system_architecture.md     # Thiết kế kiến trúc
├── state_3_features/
│   └── feature_list.md           # Danh sách tính năng
├── state_4_documents/
│   ├── brd.md                    # Business Requirements Document
│   └── srs.md                    # Software Requirements Specification
├── state_5_validation/
│   └── validation_report.json    # Báo cáo validation
├── state_6_final/
│   └── final_report.md          # Báo cáo tổng kết
└── logs/
    ├── history.jsonl            # Lịch sử build
    └── app.log                  # Application logs
```

## 🔄 Workflow

1. **Analysis**: Phân tích yêu cầu và xác định stakeholders
2. **Architecture**: Thiết kế kiến trúc hệ thống và technology stack
3. **Feature Planning**: Lập kế hoạch tính năng và prioritization
4. **Document Generation**: Sinh BRD, SRS và các tài liệu kỹ thuật
5. **Validation**: Kiểm tra chất lượng và format
6. **Final Report**: Tạo báo cáo tổng kết

## 🤖 Agents

### AnalyzerAgent
- Phân tích yêu cầu dự án
- Xác định stakeholders và objectives
- Đánh giá rủi ro và constraints

### ArchitectAgent
- Thiết kế kiến trúc hệ thống
- Recommend technology stack
- Định nghĩa components và interfaces

### FeaturePlannerAgent
- Lập kế hoạch tính năng
- Prioritization và roadmap
- User stories và acceptance criteria

### DocumentWriterAgent
- Sinh BRD và SRS
- Tài liệu kỹ thuật chuyên nghiệp
- Structured format chuẩn

### RefinerAgent
- Cải thiện nội dung dựa trên feedback
- Iterative refinement
- Quality enhancement

### ValidatorAgent
- Kiểm tra format và structure
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
Chỉnh sửa prompts trong thư mục `prompts/`:
- `analysis.txt`: Prompt cho phân tích
- `architecture.txt`: Prompt cho thiết kế kiến trúc
- `features.txt`: Prompt cho feature planning
- `brd.txt`: Prompt cho BRD generation
- `srs.txt`: Prompt cho SRS generation

### Custom Templates
Chỉnh sửa templates trong thư mục `templates/`:
- `brd_template.md`: Template cho BRD
- `srs_template.md`: Template cho SRS

## 🚀 Mở rộng

### Thêm Agent mới
1. Tạo file agent trong `agents/`
2. Implement các method cần thiết
3. Import và sử dụng trong `orchestrator.py`

### Thêm LLM Provider mới
1. Thêm logic trong `llm_manager.py`
2. Update configuration schema
3. Test với provider mới

### Thêm Document Type mới
1. Thêm prompt template
2. Update `document_writer.py`
3. Thêm validation rules

## 📋 Requirements

- Python >= 3.9
- ChromaDB
- Jinja2
- PyYAML
- Pydantic
- LLM provider packages (ollama, openai, anthropic, google-generativeai)

## 🔍 Troubleshooting

### LLM Connection Issues
- Kiểm tra API keys
- Verify network connectivity
- Check provider status

### Vector Store Issues
- Ensure ChromaDB directory writable
- Check disk space
- Verify ChromaDB installation

### Validation Errors
- Check output file permissions
- Verify markdown format
- Review validation rules

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**AI Builder** - Tự động hóa phân tích và documentation cho dự án của bạn! 🎯
