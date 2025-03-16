import sys
sys.path.append("../../agent")
from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent
from typing import Optional

class CodeExplainerAgent(AIAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        rust_path: str,
        cpp_path: str,
        max_history: int = 10,
        system_prompt: Optional[str] = None
    ):
        """
        初始化代码解释器Agent
        :param client: UnifiedLLMClient实例
        :param model_name: 使用的模型名称
        :param rust_path: Rust源代码文件路径
        :param cpp_path: C++源代码文件路径
        :param max_history: 对话历史长度
        """
        default_system_prompt = (
            "你是一个专业的代码解释专家，负责解答用户关于代码的问题。"
            "你需要清晰解释代码的功能和实现原理，重点说明语言特有的特性，"
            "并在需要时使用例子来辅助解释复杂概念。\n\n"
            "请严格按照以下JSON格式响应：\n"
            "{\n"
            "    \"explanation\": \"代码解释\",\n"
            "    \"examples\": \"相关示例\",\n"
            "    \"key_points\": \"重要知识点\"\n"
            "}\n"
            "不要写出多余的思考步骤"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt or default_system_prompt,
            model_name=model_name,
            max_history=max_history
        )
        
        self.rust_path = rust_path
        self.cpp_path = cpp_path
        # 初始化时不立即加载代码
        self.rust_code = None
        self.cpp_code = None
        self._try_load_code()

    def _try_load_code(self):
        """尝试加载代码文件，如果文件不存在则设置为 None"""
        try:
            self.cpp_code = self._load_code(self.cpp_path)
        except RuntimeError:
            self.cpp_code = None
            
        try:
            self.rust_code = self._load_code(self.rust_path)
        except RuntimeError:
            self.rust_code = None

    def _load_code(self, file_path: str) -> str:
        """读取源代码文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"文件不存在：{file_path}")
        except Exception as e:
            raise RuntimeError(f"读取文件失败：{str(e)}")

    def explain(self, question: str) -> str:
        """
        解释代码相关问题
        :param question: 用户问题
        :return: 解释内容
        """
        # 在解释前重新尝试加载代码
        self._try_load_code()
        
        if not self.cpp_code and not self.rust_code:
            return "错误：没有可用的代码文件进行解释。请先使用converter生成Rust代码。"
            
        prompt = "请解释以下代码相关的问题：\n\n"
        
        if self.cpp_code:
            prompt += f"C++代码：\n```cpp\n{self.cpp_code}\n```\n\n"
            
        if self.rust_code:
            prompt += f"Rust代码：\n```rust\n{self.rust_code}\n```\n\n"
            
        prompt += f"问题：{question}"
        
        return self.chat(
            prompt,
            max_tokens=1000,
            temperature=0.3
        )

    def interactive_explanation(self):
        """交互式解释流程"""
        print("代码解释器已启动！")
        print("输入问题来获取解释，输入'exit'退出")
        
        while True:
            question = input("\n请输入问题 > ").strip()
            
            if question.lower() == 'exit':
                break
                
            try:
                explanation = self.explain(question)
                print("\n解释：")
                print(explanation)
            except Exception as e:
                print(f"解释失败：{str(e)}")
