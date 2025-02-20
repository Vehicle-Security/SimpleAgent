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
        max_history: int = 10,
        system_prompt: Optional[str] = None
    ):
        """
        初始化代码解释器Agent
        :param client: UnifiedLLMClient实例
        :param model_name: 使用的模型名称
        :param rust_path: Rust源代码文件路径
        :param max_history: 对话历史长度
        """
        default_system_prompt = (
            "你是一个专业的Rust代码解释专家，负责解答用户关于代码的问题。请遵守以下规则：\n"
            "1. 清晰解释代码的功能和实现原理\n"
            "2. 重点说明Rust特有的语言特性\n"
            "3. 如果涉及性能相关问题，解释优化原理\n"
            "4. 使用例子来辅助解释复杂概念"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt or default_system_prompt,
            model_name=model_name,
            max_history=max_history
        )
        
        self.rust_path = rust_path
        self.current_code = self._load_rust_code()

    def _load_rust_code(self) -> str:
        """读取Rust源代码文件"""
        try:
            with open(self.rust_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"Rust文件不存在：{self.rust_path}")
        except Exception as e:
            raise RuntimeError(f"读取文件失败：{str(e)}")

    def explain(self, question: str) -> str:
        """
        解释代码相关问题
        :param question: 用户问题
        :return: 解释内容
        """
        prompt = (
            f"请解释以下Rust代码相关的问题：\n\n"
            f"代码：\n```rust\n{self.current_code}\n```\n\n"
            f"问题：{question}"
        )
        
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
