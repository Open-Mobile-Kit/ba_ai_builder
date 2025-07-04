#!/usr/bin/env python3
"""
Example usage of AI Builder
Demonstrates how to use the system programmatically
"""

import sys
from pathlib import Path

# Add the ai_builder directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import orchestrator
from core.config_manager import config


def example_ecommerce_project():
    """Example: E-commerce system build"""
    
    requirements = """
    Xây dựng hệ thống thương mại điện tử với các tính năng sau:
    
    1. Quản lý sản phẩm:
       - Thêm, sửa, xóa sản phẩm
       - Phân loại sản phẩm theo danh mục
       - Quản lý inventory và stock
       - Upload và quản lý hình ảnh sản phẩm
    
    2. Quản lý đơn hàng:
       - Tạo đơn hàng từ giỏ hàng
       - Tracking trạng thái đơn hàng
       - Quản lý giao hàng
       - Lịch sử đơn hàng
    
    3. Quản lý khách hàng:
       - Đăng ký và đăng nhập
       - Profile management
       - Wishlist và favorites
       - Review và rating sản phẩm
    
    4. Thanh toán:
       - Tích hợp cổng thanh toán (VNPay, Momo)
       - Hỗ trợ COD
       - Quản lý transactions
       - Invoice generation
    
    5. Admin dashboard:
       - Dashboard tổng quan
       - Báo cáo doanh thu
       - Quản lý users
       - System configuration
    
    Yêu cầu kỹ thuật:
    - Hỗ trợ 1000+ concurrent users
    - Response time < 2 seconds
    - Mobile-responsive design
    - Security compliance
    - Scalable architecture
    """
    
    context = {
        "budget": "200,000 USD",
        "timeline": "8 months",
        "team_size": "6 developers",
        "target_market": "Vietnam",
        "compliance": ["PCI DSS", "GDPR"],
        "integration_requirements": ["VNPay", "Momo", "GHN", "Viettel Post"]
    }
    
    print("🚀 Starting AI Builder - E-commerce Project")
    print(f"📊 Configuration: {config.llm.provider} - {config.llm.model_name}")
    print("⏳ This may take a few minutes...")
    
    try:
        # Run the build process
        result = orchestrator.build_project(requirements, context)
        
        print("\\n" + "="*80)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        print(f"📁 Output Directory: {config.get_output_path()}")
        print(f"⏱️  Total Duration: {result.get('duration', 0):.2f} seconds")
        print(f"📝 Version: {result['version']}")
        
        # Show build summary
        print("\\n📋 Build Summary:")
        for state_name, state_result in result['states'].items():
            status = state_result.get('status', 'unknown')
            file_count = len(state_result.get('files', []))
            status_emoji = "✅" if status == "completed" else "❌"
            print(f"   {status_emoji} {state_name.capitalize()}: {status} ({file_count} files)")
        
        # Show generated files
        all_files = []
        for state_result in result['states'].values():
            all_files.extend(state_result.get('files', []))
        
        print(f"\\n📄 Generated Files ({len(all_files)}):")
        for file_path in all_files:
            file_name = Path(file_path).name
            print(f"   📄 {file_name}")
        
        print("\\n🎯 Next Steps:")
        print("   1. Review generated documents in output directory")
        print("   2. Validate requirements with stakeholders")
        print("   3. Use documents for development planning")
        print("   4. Provide feedback for refinement if needed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")
        return None


def example_refinement():
    """Example: Refine documents with feedback"""
    
    feedback = """
    Cần cải thiện các điểm sau trong tài liệu:
    
    1. BRD cần thêm:
       - Chi tiết hơn về security requirements
       - Compliance requirements cho thị trường Việt Nam
       - Integration requirements với các dịch vụ local
    
    2. SRS cần thêm:
       - API specifications chi tiết
       - Database schema design
       - Performance benchmarks cụ thể
       - Error handling specifications
    
    3. Architecture cần làm rõ:
       - Microservices communication patterns
       - Caching strategy
       - Load balancing approach
       - Disaster recovery plan
    """
    
    print("🔄 Starting Document Refinement")
    
    try:
        result = orchestrator.refine_with_feedback(feedback, "documents")
        print(f"✅ Refinement completed: {result['status']}")
        return result
        
    except Exception as e:
        print(f"❌ Error during refinement: {str(e)}")
        return None


def example_custom_output_dir():
    """Example: Using custom output directory"""
    from core.config_manager import config
    
    # Set custom output directory
    custom_output = Path.home() / "Documents" / "ai_builder_projects" / "ecommerce"
    config.output.base_path = str(custom_output)
    
    # Refresh orchestrator to use new path
    orchestrator.refresh_output_paths()
    
    print(f"📁 Using custom output directory: {custom_output}")
    
    requirements = "Build a simple blog system with user authentication and post management"
    
    try:
        result = orchestrator.build_project(requirements)
        print(f"✅ Project built successfully in: {custom_output}")
        return result
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    print("🎯 AI Builder Example Usage")
    print("=" * 50)
    
    # Example 1: Full project build
    print("\\n1️⃣ Running E-commerce Project Build...")
    build_result = example_ecommerce_project()
    
    if build_result:
        print("\\n2️⃣ Running Document Refinement Example...")
        refinement_result = example_refinement()
    
    print("\\n🏁 Example completed!")
    print("Check the output directory for generated documents.")
