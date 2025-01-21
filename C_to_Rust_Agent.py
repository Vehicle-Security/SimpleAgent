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
        dict: The response from the model as a dictionary.
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
                # return generated_text
                generated_json_dict = json.loads(generated_text)
                return self.extract_rust_code(generated_json_dict)
            else:
                print(f"请求失败，状态码: {response.status_code}")
            return None            
        except requests.RequestException as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            return response
        


system_prompt = """
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



def generate_rust_file(file_path, model):
    prompt = "请把以下代码转化为rust语言\n"
    with open(file_path, "r") as file:
        prompt += file.read()
        # print(type(prompt))
        print("prompt :")
        print(prompt, "\n\n")
    Ollama_Model = OllamaModel(model = model, system_prompt = system_prompt)
    generated_text = Ollama_Model.generate_text(prompt)
    if generated_text:
        # print(type(generated_text))
        print("generated rust code :")
        print(generated_text)
        with open("rust_code.rs", "w") as file:
            file.write(generated_text) 

generate_rust_file("c_code.cpp", model = "llama3.1")