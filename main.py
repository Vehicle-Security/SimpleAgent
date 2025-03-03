import sys
sys.path.append("./agent")
sys.path.append("./demos/cpp2rust")
sys.path.append("./demos/cpp-compile-run")
sys.path.append("./demos/rust-compile-run")
sys.path.append("./demos/code-explainer")
from code_explainer_agent import CodeExplainerAgent
from unified_llm_client import UnifiedLLMClient
from agent import CodeToolboxAgent


if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )
    
    # 创建工具箱Agent
    toolbox = CodeToolboxAgent(
        client=llm_client,
        model_name="ollama-llama3",
        cpp_path="./test_code/example.cpp",
        output_dir="./test_code/output"
    )
    
    # 可选：指定输入文件
    input_file = "./test_code/input"  # 如果代码需要输入文件，在这里指定
    
    # 启动交互式会话
    toolbox.interactive_session(input_file)
