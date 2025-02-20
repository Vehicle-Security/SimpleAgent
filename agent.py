import sys
sys.path.append("./agent")
sys.path.append("./demos/cpp2rust")
sys.path.append("./demos/cpp-compile-run")
sys.path.append("./demos/rust-compile-run")
from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent
from code_converter_agent import CodeConverterAgent
from code_modifier_agent import CodeModifierAgent
from typing import Optional, Dict, Any
import os

class CodeToolboxAgent(AIAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        cpp_path: str,
        output_dir: str,
        max_history: int = 10
    ):
        """
        工具箱Agent
        :param client: UnifiedLLMClient实例
        :param model_name: 使用的模型名称
        :param cpp_path: C++源代码路径
        :param output_dir: 输出目录
        :param max_history: 对话历史长度初始化代码
        """
        system_prompt = (
            "你是一个智能代码助手，负责理解用户需求并选择合适的工具。可用的工具有：\n"
            "1. 代码转换器(converter): 将C++代码转换为Rust代码\n"
            "2. 代码修正器(modifier): 诊断和修复Rust代码问题\n"
            "请根据用户输入判断应该使用哪个工具，并按以下格式响应：\n"
            "[TOOL_CHOICE]\n"
            "工具名称: converter或modifier\n"
            "原因: 选择该工具的理由\n"
            "[ACTION]\n"
            "建议的具体操作"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt,
            model_name=model_name,
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
            )
        }
    
    def _parse_tool_choice(self, response: str) -> Dict[str, str]:
        """解析工具选择响应"""
        import re
        
        tool_match = re.search(r'\[TOOL_CHOICE\](.*?)\[ACTION\]', response, re.DOTALL)
        action_match = re.search(r'\[ACTION\](.*)', response, re.DOTALL)
        
        if not tool_match or not action_match:
            raise ValueError("无效的响应格式")
            
        tool_section = tool_match.group(1)
        tool_name = re.search(r'工具名称:\s*(converter|modifier)', tool_section)
        
        if not tool_name:
            raise ValueError("未找到有效的工具名称")
            
        return {
            "tool": tool_name.group(1),
            "action": action_match.group(1).strip()
        }
    
    def process_request(self, user_input: str) -> str:
        """
        处理用户请求
        :param user_input: 用户输入
        :return: 处理结果
        """
        # 让模型选择工具
        response = self.chat(
            f"用户请求：{user_input}\n请选择合适的工具并说明原因",
            max_tokens=500,
            temperature=0.3
        )
        
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
                    instruction=action
                )
                return f"代码修正{'成功' if success else '失败'}: {output}"
                
        except Exception as e:
            return f"处理失败: {str(e)}"
            
    def interactive_session(self):
        print("代码工具箱助手启动！")
        print("可用命令：")
        print("- 输入需求描述来使用工具")
        print("- 输入'switch to [converter/modifier]'来直接使用特定工具")
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
                    else:
                        self.tools[tool_name].interactive_fixing()
                    continue
                else:
                    print("无效的工具名称")
                    continue
            
            result = self.process_request(user_input)
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
    
    # 启动交互式会话
    toolbox.interactive_session()
