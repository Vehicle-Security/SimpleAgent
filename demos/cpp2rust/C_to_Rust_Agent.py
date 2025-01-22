from termcolor import colored
import os
from dotenv import load_dotenv
load_dotenv()
### Models
import requests
import json
import operator


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
        


class C2RustConverter:
    def __init__(self, model="llama3.1"):
        """
        初始化C到Rust的转换器
        
        Parameters:
        model (str): 使用的Ollama模型名称，默认为llama3.1
        """
        self.model = model
        self.system_prompt = """
        You are an agent that specialized in converting C code to rust code.
        Given a user query,
        you will try to identify the code portion of the query,
        and then convert the code portion into rust language 
        You will generate the following JSON response:

        "code" : {
            "type" : "Rust",
            "content" " [
                "code_content"
            ]
        }
        """
        self.ollama_model = OllamaModel(
            model=self.model, 
            system_prompt=self.system_prompt
        )

    def convert_file(self, input_file_path, output_file_path="rust_code.rs"):
        """
        将C/C++文件转换为Rust文件
        
        Parameters:
        input_file_path (str): 输入的C/C++文件路径
        output_file_path (str): 输出的Rust文件路径，默认为'rust_code.rs'
        
        Returns:
        bool: 转换是否成功
        """
        try:
            prompt = "请把以下代码转化为rust语言\n"
            with open(input_file_path, "r") as file:
                prompt += file.read()
                print("prompt:")
                print(prompt, "\n\n")

            generated_text = self.ollama_model.generate_text(prompt)
            
            if generated_text:
                print("generated rust code:")
                print(generated_text)
                with open(output_file_path, "w") as file:
                    file.write(generated_text)
                return True
            return False
            
        except Exception as e:
            print(f"转换过程中出现错误: {str(e)}")
            return False

    def convert_code(self, code_string, output_file_path=None):
        """
        直接转换C/C++代码字符串为Rust代码
        
        Parameters:
        code_string (str): 输入的C/C++代码字符串
        output_file_path (str, optional): 如果提供，将结果保存到文件
        
        Returns:
        str: 生成的Rust代码
        """
        prompt = "请把以下代码转化为rust语言\n" + code_string
        generated_text = self.ollama_model.generate_text(prompt)
        
        if generated_text and output_file_path:
            with open(output_file_path, "w") as file:
                file.write(generated_text)
                
        return generated_text

# 使用示例
if __name__ == "__main__":
    converter = C2RustConverter(model="llama3.1")
    converter.convert_file("c_code.cpp")