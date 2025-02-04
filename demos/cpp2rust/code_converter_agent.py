from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent
import os
import re
from typing import Optional

class CodeConverterAgent(AIAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        input_path: str,
        output_dir: str,
        max_history: int = 10,
        system_prompt: Optional[str] = None
    ):
        """
        初始化代码转换AI Agent
        :param client: 配置好的 UnifiedLLMClient 实例
        :param model_name: 使用的模型名称
        :param input_path: C++源代码文件路径
        :param output_dir: 输出目录
        :param max_history: 保留的对话历史长度
        """
        # 设置默认系统提示
        default_system_prompt = (
            "你是一个专业的代码转换专家，负责将C++代码转换为Rust代码，并生成对应的Cargo.toml文件。\n"
            "请遵守以下规则：\n"
            "1. 保持代码逻辑和结构一致\n"
            "2. 使用Rust的最佳实践\n"
            "3. 生成的toml需包含必要依赖\n"
            "4. 按以下格式响应：\n"
            "   [RUST_CODE]\n"
            "   ```rust\n"
            "   生成的Rust代码\n"
            "   ```\n"
            "   [TOML]\n"
            "   ```toml\n"
            "   生成的TOML内容\n"
            "   ```"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt or default_system_prompt,
            model_name=model_name,
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
        """
        解析模型响应，提取Rust代码和TOML内容
        返回格式：{"rust": str, "toml": str}
        """
        # 使用正则表达式匹配代码块
        rust_match = re.search(r'\[RUST_CODE\].*?```rust(.*?)```', response, re.DOTALL)
        toml_match = re.search(r'\[TOML\].*?```toml(.*?)```', response, re.DOTALL)

        return {
            "rust": rust_match.group(1).strip() if rust_match else "",
            "toml": toml_match.group(1).strip() if toml_match else ""
        }

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
        if not parsed["rust"]:
            raise ValueError("未检测到有效的Rust代码块")
        if not parsed["toml"]:
            print("警告：未检测到TOML配置，将生成空Cargo.toml")
        self._save_generated_files(parsed["rust"], parsed["toml"])
        
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
    )

    # 执行自动转换
    # result = converter.convert()
    
    # 启动交互式转换流程
    converter.interactive_conversion()