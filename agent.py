import sys
sys.path.append("./agent")
sys.path.append("./demos/cpp2rust")
sys.path.append("./demos/cpp-compile-run")
sys.path.append("./demos/rust-compile-run")
sys.path.append("./demos/code-explainer")
from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent
from code_converter_agent import CodeConverterAgent
from code_modifier_agent import CodeModifierAgent
from code_explainer_agent import CodeExplainerAgent
from typing import Optional, Dict, Any
import os
from rag_agent import RAGAgent

class CodeToolboxAgent(RAGAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        cpp_path: str,
        output_dir: str,
        knowledge_base_path: str = "./knowledge_base",
        embedding_model: str = "all-MiniLM-L6-v2",
        max_history: int = 10
    ):
        """
        初始化带RAG功能的工具箱Agent
        :param client: UnifiedLLMClient实例
        :param model_name: 使用的模型名称
        :param cpp_path: C++源代码路径
        :param output_dir: 输出目录
        :param knowledge_base_path: 知识库目录路径
        :param embedding_model: 使用的embedding模型名称
        :param max_history: 对话历史长度初始化代码
        """
        
        system_prompt = (
            "你是一个智能代码助手，负责理解用户需求并选择合适的工具。\n\n"
            "可用工具说明：\n"
            "1. converter: C++代码转换为Rust代码\n"
            "2. modifier: 诊断和修复Rust代码问题\n"
            "3. explainer: 解释代码相关问题\n\n"
            "请严格按照以下JSON格式响应：\n"
            "{\n"
            "    \"tool\": \"converter\",  // 必须是 converter、modifier 或 explainer\n"
            "    \"reason\": \"选择该工具的理由\",\n"
            "    \"action\": \"建议的具体操作\"\n"
            "}"
        )
        
        super().__init__(
            client=client,
            model_name=model_name,
            knowledge_base_path=knowledge_base_path,
            embedding_model=embedding_model,
            system_prompt=system_prompt,
            max_history=max_history
        )
        
        self.cpp_path = cpp_path
        self.output_dir = output_dir
        self.rust_path = os.path.join(
            output_dir, 
            os.path.splitext(os.path.basename(cpp_path))[0] + ".rs"
        )
        
        # 初始化工具
        self.tools = self._initialize_tools(client, model_name)
        
    def _initialize_tools(
        self, 
        client: UnifiedLLMClient, 
        model_name: str
    ) -> Dict[str, Any]:
        """初始化工具集"""
        return {
            "converter": CodeConverterAgent(
                client=client,
                model_name=model_name,
                input_path=self.cpp_path,
                output_dir=self.output_dir
            ),
            "modifier": CodeModifierAgent(
                client=client,
                model_name=model_name,
                rust_path=self.rust_path,
                cpp_path=self.cpp_path
            ),
            "explainer": CodeExplainerAgent(
                client=client,
                model_name=model_name,
                rust_path=self.rust_path,
                cpp_path=self.cpp_path
            )
        }
    
    def _parse_tool_choice(self, response: str) -> Dict[str, str]:
        """解析工具选择响应"""
        try:
            import json
            result = json.loads(response)
            if not all(k in result for k in ["tool", "reason", "action"]):
                raise ValueError("响应缺少必要字段")
            return result
        except json.JSONDecodeError:
            raise ValueError("无效的JSON格式")
    
    def process_request(self, user_input: str, input_file: Optional[str] = None) -> str:
        """
        处理用户请求
        :param user_input: 用户输入
        :param input_file: 可选的输入文件路径
        :return: 处理结果
        """
        # 让模型选择工具
        response = self.chat(
            f"用户请求：{user_input}\n请选择合适的工具并说明原因",
            max_tokens=500,
            temperature=0.3
        )
        print(response)
        try:
            # 解析工具选择
            choice = self._parse_tool_choice(response)
            tool_name = choice["tool"]
            action = choice["action"]
            
            print(f"\n选择工具: {tool_name}")
            print(f"建议操作: {action}\n")
            
            # 执行工具操作
            if tool_name == "converter":
                result = self.tools["converter"].convert(
                    additional_instructions=action
                )
                return "代码转换完成，已保存到输出目录"
                
            elif tool_name == "modifier":
                success, output = self.tools["modifier"].diagnose_and_fix(
                    instruction=action,
                    input_file=input_file
                )
                return f"代码修正{'成功' if success else '失败'}: {output}"
                
            elif tool_name == "explainer":
                explanation = self.tools["explainer"].explain(action)
                return f"解释如下：\n{explanation}"
                
        except Exception as e:
            return f"处理失败: {str(e)}"
            
    def interactive_session(self, input_file: Optional[str] = None):
        """
        交互式会话
        :param input_file: 可选的输入文件路径，用于代码运行
        """
        print("代码工具箱助手启动！")
        print("可用命令：")
        print("- 输入需求描述来使用工具")
        print("- 输入'switch to [converter/modifier/explainer]'来直接使用特定工具")
        print("- 输入'exit'退出")
        
        while True:
            user_input = input("\n请输入需求 > ").strip()
            
            if user_input.lower() == 'exit':
                break
                
            if user_input.lower().startswith('switch to '):
                tool_name = user_input.lower().split()[-1]
                if tool_name in self.tools:
                    print(f"\n切换到{tool_name}交互模式...")
                    if tool_name == 'converter':
                        self.tools[tool_name].interactive_conversion()
                    elif tool_name == 'modifier':
                        self.tools[tool_name].interactive_fixing(input_file)
                    else:
                        self.tools[tool_name].interactive_explanation()
                    continue
                else:
                    print("无效的工具名称")
                    continue
            
            result = self.process_request(user_input, input_file)
            print(result)

# ===== 使用示例 =====
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

