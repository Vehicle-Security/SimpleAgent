import sys
sys.path.append("./agent")
sys.path.append("./demos/cpp2rust")
sys.path.append("./demos/cpp-compile-run")
sys.path.append("./demos/rust-compile-run")
sys.path.append("./demos/code-explainer")
from unified_llm_client import UnifiedLLMClient
from agent import CodeToolboxAgent
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3.1", 
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )
    llm_client.add_model(
        model_name="ollama-deepssek-r1:8b", 
        config=llm_client.configs["ollama"],
        model="deepseek-r1:8b"
    )
    
    # 从环境变量获取 API key
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
    llm_client.add_model(
        model_name="deepseek-deepseek-chat",
        config=llm_client.configs["deepseek"],
        api_key=DEEPSEEK_API_KEY,
        model="deepseek-chat"
    )
    
    # 创建工具箱Agent（使用改进的RAG功能）
    toolbox = CodeToolboxAgent(
        client=llm_client,
        model_name="deepseek-deepseek-chat",
        cpp_path="./test_code/example.cpp",
        output_dir="./test_code/output",
        knowledge_base_path="./knowledge_base",
        embedding_model="all-MiniLM-L6-v2"  # 指定embedding模型
    )
    
    # 可选：指定输入文件
    input_file = "./test_code/example.in"
    
    # 启动交互式会话
    toolbox.interactive_session(input_file)
