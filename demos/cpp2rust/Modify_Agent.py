import subprocess
import requests
import json

class OllamaModel:
    def __init__(self, model, system_prompt, temperature = 0, stop = None):
        """
        Initializes the OllamaModel with the given parameters.

        Parameters:
        model (str): The name of the model to use.
        system_prompt (str): The system prompt to use.
        temperature (float): The temperature setting for the model.
        stop (str): The stop token for the model.
        """
        self.model_url = "http://localhost:11434/api/generate"
        self.temperature = temperature
        self.model = model
        self.system_prompt = system_prompt
        self.headers = {"Content-Type": "application/json"}
        self.stop = stop

    def extract_rust_code(self, code_dict):
        if code_dict is None:
            return "请求失败，未获取到有效数据"
        try:
            # 将Python字典转换为JSON字符串
            json_str = json.dumps(code_dict, ensure_ascii=False)
            # 解析JSON字符串为Python字典
            data = json.loads(json_str)
            # 提取出Rust代码内容
            rust_code_lines = data.get('code', {}).get('content', [])
            # 将Rust代码行合并成一个字符串
            rust_code = '\n'.join(rust_code_lines)
            # 输出Rust代码
            # print(rust_code)
            return rust_code
        except json.JSONDecodeError as e:
            # print(f"JSON解析失败: {e}")
            return f"JSON解析失败：{e}"

    def generate_text(self, prompt):
        """
        Generates a response from the Ollama model based on the provided prompt.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        dict: The response from the model.
        """
        payload = {
            "model": self.model,
            "format": "json",
            "prompt": prompt,
            "system": self.system_prompt,
            "stream": False,
            "temperature": self.temperature,
            "stop": self.stop
        }
        try:
            response = requests.post(
                self.model_url,
                headers = self.headers,
                data = json.dumps(payload)
            )
            if response.status_code == 200:
                # 按行分割响应内容
                response_lines = response.text.splitlines()
                generated_text = ""
                for line in response_lines:
                    try:
                        result = json.loads(line)
                        # print(result)
                        # 假设 Ollama 的响应包含生成的文本在 'response' 字段中
                        generated_text += result.get('response', "")
                    except json.JSONDecodeError:
                        continue
                # print(generated_text)
                generated_json_dict = json.loads(generated_text)
                # print(type(generated_json_dict))
                return generated_json_dict
            else:
                print(f"请求失败，状态码: {response.status_code}")
            return None            
        except requests.RequestException as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            return response
        
    def generate_rust_code(self, prompt):
        """
        Generates a response from the Ollama model based on the provided prompt.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        str: The response code from the model.
        """
        generated_json_dict = self.generate_text(prompt)
        generate_rust_code = self.extract_rust_code(generated_json_dict)
        return generate_rust_code

class RustCodeModifier:
    def __init__(self, model="llama3.1"):
        self.model = model
        self.system_prompt = """
        You are an agent that specialized in fixing error rust code.
        Given a user query that contains oridinal rust code and error message,
        you will try to fix the given rust code according to the error message.
        You will generate the following JSON response:

        "code" : {
                    "type" : "Rust",
                    "content" : [
                        "code_content"
                    ]
                },
        "explanation" : "explanation"
        """
        self.ollama_model = OllamaModel(
            model = self.model,
            system_prompt = self.system_prompt
        )
    
    def rust_compiler(self, file_path):
        """
        Compile rust code

        Parameters:
        file_path(str)：需要编译的rust代码的path

        Rerturns:
        pair：
            success_flag(int)： 1 for success, 0 for failure
            result_message(str)：Compilation output or error message
        """
        try:
            # 使用 subprocess 模块的 run 方法调用 bash 命令
            result = subprocess.run(['rustc', file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print("编译成功：", result.stdout.decode())
            return 1, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            # print("编译失败：", e.stderr.decode())
            return 0, e.stderr.decode()
        
    def rust_runner(self, executable_path):
        """
        Run executable file

        Parameters:
        file_path(str)：需要运行的rust代码的path

        Rerturns:
        pair：
            success_flag(int)： 1 for success, 0 for failure
            result_message(str)：Runtime output or error message
        """
        try:
            # 使用 subprocess 模块的 run 方法调用 bash 命令
            result = subprocess.run([executable_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print("运行成功：", result.stdout.decode())
            return 1, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            # print("运行失败：", e.stderr.decode())
            return 0, e.stderr.decode()

    def modify(self, file_path):
        """
        Modifies Rust code based on compilation and runtime errors.
        
        Parameters:
        file_path (str): Path to the Rust source code file
        
        Returns:
        tuple: (success_flag, result_message, modified_code)
            - success_flag (int): 1 for success, 0 for failure
            - result_message (str): Compilation/runtime output or error message
            - modified_code (str): Modified code if changes were made, None otherwise
        """
        # Read the original code
        with open(file_path, 'r') as file:
            original_code = file.read()

        # First try to compile the code
        compile_flag, compile_result = self.rust_compiler(file_path=file_path)
        
        if compile_flag == 0:  # Compilation failed
            # Generate prompt for the LLM to fix compilation errors
            prompt = f"""
Here is the original Rust code:
{original_code}

The code failed to compile with this error:
{compile_result}
Please fix the code and explain the changes.
            """
            print("prompt : ", prompt)
            # Get fixed code from LLM
            # print(f"model = self.ollama_model {self.ollama_model}")
            # prompt = "hi" 
            # print(f"model={self.model}")
            # ollama_model_modify = OllamaModel(model="llama3.1", system_prompt="")
            # generated_code = ollama_model_modify.generate_rust_code(prompt=prompt)
            fixed_code = self.ollama_model.generate_rust_code(prompt)
            print("fixed_code : ", fixed_code)
            with open("rust_code.rs", "w") as file:
                file.write(fixed_code)
            return 0, compile_result, fixed_code
            
        else:  # Compilation succeeded
            executable_path = file_path.rsplit('.', 1)[0]  # Remove .rs extension
            run_flag, run_result = self.rust_runner(executable_path)
            
            if run_flag == 0:  # Runtime error
                # Generate prompt for the LLM to fix runtime errors
                prompt = f"""
                Here is the original Rust code:
                {original_code}

                The code compiled successfully but failed during execution with this error:
                {run_result}
                Please fix the code and explain the changes.
                """
                print("prompt : ", prompt)
                # Get fixed code from LLM
                fixed_code = self.ollama_model.generate_rust_code(prompt)
                print("fixed_code : ", fixed_code)
                with open("rust_code.rs", "w") as file:
                    file.write(fixed_code)
                return 0, run_result, fixed_code
                
            else:  # Everything succeeded
                print("run_result : ", run_result)
                return 1, run_result, None


model = "llama3.1"
system_prompt_chat = """
Chat with me
You will generate the following JSON response:
"response" : "your response to the given request"
"""

# 使用示例
if __name__ == "__main__":
    modifier = RustCodeModifier(model="llama3.1")
    modifier.modify("./rust_code.rs")

"""test Ollama Model"""
# ollama_model_chat = OllamaModel(model=model, system_prompt=system_prompt_chat)
# if __name__ == "__main__":
#     while True:
#         prompt = input("Ask me something : ")
#         if prompt.lower() == "exit":
#             break
#         generated_text = ollama_model_chat.generate_text(prompt)
#         if generated_text:
#             print(generated_text)

"""test modifier.rust_compiler"""
# modifier = RustCodeModifier(model="llama3.1")
# f, res = modifier.rust_compiler("./rust_code.rs")
# if f == 0:
#     print("编译失败：")
# else:
#     print("编译成功：")
# print(type(res))
# print(res)

"""test modifier.rust_runner"""
# modifier = RustCodeModifier(model="llama3.1")
# f, res = modifier.rust_runner("./rust_code")
# if f == 0:
#     print("运行失败：")
# else:
#     print("运行成功：")
# print(type(res))
# print(res)

"""test modifier.modifier"""
# modifier = RustCodeModifier(model="llama3.1")
# f, res, code = modifier.modifier("./rust_code.rs")
# if(f == 1):
#     print("编译成功")
# else:
#     print("编译失败")
#     print(res)
#     print("修改后代码：")
#     print(code)

"""test"""
# system_prompt_modify = """
# You are an agent that specialized in fixing error rust code.
#     Given a user query that contains error message,
#     you will try to fix the given rust code according to the error message.
#     You will generate the following JSON response:

#     "code" : {
#                 "type" : "Rust",
#                 "content" : [
#                     "code_content"
#                 ]
#             },
#     "explanation" : "explanation"
# """
# prompt = """
# Here is the original Rust code:
# fn main() {
#     let mut n: i32 = 114515;
#     println!("{}", n - 1);


# The code failed to compile with this error:
# error: this file contains an unclosed delimiter
#  --> ./rust_code.rs:3:28
#   |
# 1 | fn main() {
#   |           - unclosed delimiter
# 2 |     let mut n: i32 = 114515;
# 3 |     println!("{}", n - 1);
#   |                            ^

# error: aborting due to previous error


# Please fix the code and explain the changes."""
# ollama_model_modify = OllamaModel(model=model, system_prompt=system_prompt_modify)
# generated_code = ollama_model_modify.generate_rust_code(prompt=prompt)
# print(generated_code)