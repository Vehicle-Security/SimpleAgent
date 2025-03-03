import sys
sys.path.append("../../agent")
from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent
import sys
sys.path.append("../rust-compile-run")
sys.path.append("../cpp-compile-run")
from Rust import Rust
from Cpp import Cpp
import re
from typing import Optional, Tuple

class CodeModifierAgent(AIAgent):
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
        初始化代码修正AI Agent
        :param client: 配置好的 UnifiedLLMClient 实例
        :param model_name: 使用的模型名称
        :param rust_path: Rust源代码文件路径
        :param cpp_path: 对应的C++源代码文件路径
        :param max_history: 保留的对话历史长度
        """
        default_system_prompt = (
            "你是一个专业的代码修正专家，负责诊断和修复Rust代码问题。请遵守以下规则：\n"
            "1. 根据编译/运行时错误分析问题\n"
            "2. 保持与原始C++代码的逻辑一致性\n"
            "3. 使用Rust的安全最佳实践\n"
            "4. 响应格式(特别注意，必须严格遵循响应格式进行输出，[ANALYSIS]和[MODIFIED_CODE]部分不能进行包括翻译在内的任何改动)：\n"
            "   [ANALYSIS]\n"
            "   问题分析...\n"
            "   [MODIFIED_CODE]\n"
            "   ```rust\n"
            "   修正后的代码\n"
            "   ```"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt or default_system_prompt,
            model_name=model_name,
            max_history=max_history
        )
        
        self.rust_path = rust_path
        self.cpp_path = cpp_path
        self.rust_runner = Rust(rust_path)
        self.cpp_runner = Cpp(cpp_path)
        self.max_retry = 5  # 最大重试次数

    def _compile_and_run_rust(self, input_file=None) -> Tuple[int, str]:
        """编译并运行Rust代码"""
        compile_flag, compile_output = self.rust_runner.rust_compile()
        if compile_flag != 0:
            return 1, f"编译错误：\n{compile_output}"
        
        run_flag, run_output = self.rust_runner.rust_run(input_file)
        return run_flag, run_output

    def _compile_and_run_cpp(self, input_file=None) -> Tuple[int, str]:
        """编译并运行C++代码"""
        compile_flag, compile_output = self.cpp_runner.cpp_compile()
        if compile_flag != 0:
            return 1, f"C++编译错误：\n{compile_output}"
        
        run_flag, run_output = self.cpp_runner.cpp_run(input_file)
        return run_flag, run_output

    def _get_code_diff(self, rust_out: str, cpp_out: str) -> str:
        """生成输出差异分析"""
        return (
            "输出不一致：\n"
            f"Rust 输出：\n{rust_out}\n"
            f"C++ 输出：\n{cpp_out}\n"
            "请确保逻辑一致"
        )

    def _parse_response(self, response: str) -> str:
        """解析模型响应中的代码"""
        code_match = re.search(r'\[MODIFIED_CODE\].*?```rust(.*?)```', response, re.DOTALL)
        if not code_match:
            raise ValueError("未检测到有效的代码块")
        return code_match.group(1).strip()

    def _update_rust_code(self, new_code: str):
        """更新Rust代码文件"""
        try:
            with open(self.rust_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            # 重新初始化runner以加载新代码
            self.rust_runner = Rust(self.rust_path)
        except Exception as e:
            raise RuntimeError(f"更新代码失败：{str(e)}")

    def diagnose_and_fix(self, instruction: Optional[str] = None, input_file: Optional[str] = None) -> Tuple[bool, str]:
        """
        执行诊断和修复流程
        :param instruction: 可选的人工修正指令
        :param input_file: 可选的输入文件路径
        :return: (是否成功, 最终输出)
        """
        for attempt in range(self.max_retry):
            print(f"\n=== 第{attempt+1}次尝试 ===")
            
            # 步骤1：编译运行Rust
            rust_status, rust_output = self._compile_and_run_rust(input_file)
            
            # 步骤2：如果Rust运行成功，验证与C++的一致性
            if rust_status == 0:
                print("Rust编译和运行成功")
                cpp_status, cpp_output = self._compile_and_run_cpp(input_file)
                if cpp_status != 0:
                    print(f"C++代码验证失败：\n{cpp_output}")
                    return False, f"C++代码验证失败：{cpp_output}"
                
                if rust_output.strip() == cpp_output.strip():
                    return True, rust_output
                
                # 输出不一致时生成差异提示并读取两个源文件
                diff_analysis = self._get_code_diff(rust_output, cpp_output)
                with open(self.cpp_path, 'r', encoding='utf-8') as f:
                    cpp_code = f.read()
                with open(self.rust_path, 'r', encoding='utf-8') as f:
                    rust_code = f.read()
                
                print(f"\n输出不一致：\n{diff_analysis}")
                prompt = (
                    f"原始cpp代码：\n{cpp_code}\n"
                    f"需要修正的rust代码：\n{rust_code}\n"
                    f"输出不一致：\n{diff_analysis}\n"
                    "请确保两者逻辑相同"
                )
            else:
                print(f"\nRust编译/运行错误：\n{rust_output}")
                prompt = f"编译/运行时错误：\n{rust_output}\n请分析并修正代码"
            
            # 添加人工指令
            if instruction:
                prompt += f"\n附加要求：{instruction}"
            
            # 调用LLM获取修正方案
            try:
                response = self.chat(prompt, max_tokens=2000, temperature=0.3)
                print("response:\n", response)
                new_code = self._parse_response(response)
                self._update_rust_code(new_code)
                
                # 记录到对话历史
                self.message_history.append({
                    "role": "system",
                    "content": f"第{attempt+1}次修正后的代码片段：\n{new_code[:300]}..."
                })
            except Exception as e:
                return False, f"修正失败：{str(e)}"
        
        return False, f"经过{self.max_retry}次尝试仍未解决问题"

    def interactive_fixing(self, input_file: Optional[str] = None):
        """
        交互式修正流程
        :param input_file: 可选的输入文件路径
        """
        print("开始自动诊断...")
        success, output = self.diagnose_and_fix(input_file=input_file)
        
        if success:
            print("\n初始修正成功！输出结果：")
            print(output)
            return

        while True:
            print("\n当前问题：")
            print(self.message_history[-1]["content"])
            
            print("\n选项：")
            print("1. 自动重试修正")
            print("2. 输入修正指令")
            print("3. 查看完整代码")
            print("4. 退出")
            
            choice = input("请选择操作：")
            
            if choice == '1':
                success, output = self.diagnose_and_fix(input_file=input_file)
                if success:
                    print("\n修正成功！输出结果：")
                    print(output)
                    break
            elif choice == '2':
                instruction = input("请输入修正指令：")
                success, output = self.diagnose_and_fix(instruction=instruction, input_file=input_file)
                if success:
                    print("\n修正成功！输出结果：")
                    print(output)
                    break
            elif choice == '3':
                with open(self.rust_path, 'r') as f:
                    print(f"\n当前Rust代码：\n{f.read()}")
            elif choice == '4':
                print("终止修正流程")
                break
            else:
                print("无效输入，请重新选择")

# ===== 使用示例 =====
if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )

    # 创建修正Agent
    modifier = CodeModifierAgent(
        client=llm_client,
        model_name="ollama-llama3",
        rust_path="../../test_code/output/example.rs",
        cpp_path="../../test_code/example.cpp"
    )

    # 指定输入文件进行修正（示例）
    input_file = "../../test_code/input"  # 可选的输入文件
    modifier.interactive_fixing(input_file)