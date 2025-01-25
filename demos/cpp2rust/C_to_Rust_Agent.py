from OllamModel import OllamaModel

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
            "content" : [
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

            generated_code = self.ollama_model.generate_rust_code(prompt)
            
            if generated_code:
                print("generated rust code:")
                print(generated_code)
                with open(output_file_path, "w") as file:
                    file.write(generated_code)
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
        generated_code = self.ollama_model.generate_rust_code(prompt)
        
        if generated_code and output_file_path:
            with open(output_file_path, "w") as file:
                file.write(generated_code)
                
        return generated_code

# 使用示例
if __name__ == "__main__":
    converter = C2RustConverter(model="llama3.1")
    converter.convert_file("./c_code.cpp")