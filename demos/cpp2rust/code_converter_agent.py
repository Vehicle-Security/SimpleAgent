import sys
sys.path.append("../../agent")
from unified_llm_client import UnifiedLLMClient
from rag_agent import RAGAgent
import os
import re
from typing import Optional

class CodeConverterAgent(RAGAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        input_path: str,
        output_dir: str,
        knowledge_base_path: str,
        embedding_model: str = "all-MiniLM-L6-v2",
        max_history: int = 10,
        system_prompt: Optional[str] = None
    ):
        """
        初始化代码转换AI Agent
        :param client: 配置好的 UnifiedLLMClient 实例
        :param model_name: 使用的模型名称
        :param input_path: C++源代码文件路径
        :param output_dir: 输出目录
        :param knowledge_base_path: 知识库路径
        :param embedding_model: 嵌入模型
        :param max_history: 保留的对话历史长度
        """
        # 设置默认系统提示
        default_system_prompt = (
            "你是一个精通C++和Rust编程语言的代码转换专家，负责将C++代码转换为Rust代码。"
            "你需要保持代码逻辑和结构一致，使用Rust的最佳实践，并生成对应的Cargo.toml文件。\n\n"
            "请严格按照以下JSON格式响应：\n"
            "{\n"
            "    \"rust_code\": \"生成的Rust代码\",\n"
            "    \"cargo_toml\": \"生成的Cargo.toml内容\",\n"
            "    \"explanation\": \"转换说明\"\n"
            "}\n"
            "不要写出多余的思考步骤"
        )
        
        super().__init__(
            client=client,
            model_name=model_name,
            knowledge_base_path=knowledge_base_path,
            embedding_model=embedding_model,
            system_prompt=system_prompt or default_system_prompt,
            max_history=max_history
        )
        # print("system prompt : \n", self.system_prompt, "\n")
        self.input_path = input_path
        self.output_dir = output_dir
        self.current_rust_code = ""  # 用于保存当前生成的代码
        os.makedirs(self.output_dir, exist_ok=True)

    def load_cpp_code(self) -> str:
        """读取C++源代码文件"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"输入文件不存在：{self.input_path}")
        except Exception as e:
            raise RuntimeError(f"读取文件失败：{str(e)}")

    def _parse_response(self, response: str) -> dict:
        """解析模型响应"""
        try:
            import json
            result = json.loads(response)
            if not all(k in result for k in ["rust_code", "cargo_toml"]):
                raise ValueError("响应缺少必要字段")
            return result
        except json.JSONDecodeError:
            raise ValueError("无效的JSON格式")

    def _save_generated_files(self, rust_code: str, toml_content: str):
        """保存生成的文件"""
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        rust_path = os.path.join(self.output_dir, f"{base_name}.rs")
        toml_path = os.path.join(self.output_dir, "Cargo.toml")
        print("rust path : ", rust_path, "\n")
        print("toml path : ", toml_path, "\n")
        print("rust code : \n", rust_code, "\n")
        print("toml content : \n", toml_content, "\n")
        # 保存Rust代码
        if rust_code:
            with open(rust_path, 'w', encoding='utf-8') as f:
                f.write(rust_code)
            self.current_rust_code = rust_code  # 更新当前代码

        # 保存TOML
        if toml_content:
            with open(toml_path, 'w', encoding='utf-8') as f:
                f.write(toml_content)

    def convert(self, additional_instructions: Optional[str] = None):
        """
        执行代码转换
        :param additional_instructions: 额外的转换说明（用于多轮对话）
        """
        # 读取C++代码
        cpp_code = self.load_cpp_code()
        # print("cpp code : ", cpp_code)
        
        # 构造提示语
        prompt = f"请将以下C++代码转换为Rust代码：\n```cpp\n{cpp_code}\n```"
        if additional_instructions:
            prompt += f"\n附加要求：{additional_instructions}"
        
        # 调用模型生成
        response = self.chat(
            prompt,
            max_tokens=2000,
            temperature=0.2  # 使用较低温度保证稳定性
        )
        
        # 解析并保存结果
        parsed = self._parse_response(response)
        # print("parsed : ", parsed)
        if not parsed["rust_code"]:
            raise ValueError("未检测到有效的Rust代码块")
        if not parsed["cargo_toml"]:
            print("警告：未检测到TOML配置，将生成空Cargo.toml")
        self._save_generated_files(parsed["rust_code"], parsed["cargo_toml"])
        
        # 添加生成结果到历史（保持上下文）
        self.message_history.append({
            "role": "system",
            "content": f"上次生成的Rust代码：\n{self.current_rust_code[:500]}..."
        })
        
        return parsed

    def interactive_conversion(self):
        """交互式转换流程"""
        print("开始代码转换...")
        self.convert()
        
        while True:
            print("\n当前生成的Rust代码已保存至输出目录")
            print("输入后续指令（例如：'修复编译错误'、'优化性能'），或输入'exit'结束：")
            user_input = input("> ")
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            try:
                self.convert(additional_instructions=user_input)
                print("已根据新指令更新代码！")
            except Exception as e:
                print(f"转换失败：{str(e)}")

# ===== 使用示例 =====
if __name__ == "__main__":
    # 初始化客户端
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )

    # 创建代码转换Agent
    converter = CodeConverterAgent(
        client=llm_client,
        model_name="ollama-llama3",
        input_path="example.cpp",
        output_dir="./output",
        knowledge_base_path="",
        embedding_model="all-MiniLM-L6-v2",
    )

    # 执行自动转换
    # result = converter.convert()
    
    # 启动交互式转换流程
    converter.interactive_conversion()