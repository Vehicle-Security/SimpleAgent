import sys
sys.path.append("../rust-compile-run")
from Rust import Rust
from OllamModel import OllamaModel

class RustCodeModifier:
    def __init__(self, model="llama3.1", file_path=""):
        self.file_path = file_path
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
        self.rust = Rust(file_path=self.file_path)

    def modify(self, file_path):
        """
        Modifies Rust code based on compilation and runtime errors.
        
        Parameters:
        file_path (str): Path to the Rust source code file
        
        Returns:
        tuple: (success_flag, result_message, modified_code)
            - success_flag (int): 0 for success, 1 for failure
            - result_message (str): Compilation/runtime output or error message
            - modified_code (str): Modified code if changes were made, None otherwise
        """
        # Read the original code
        with open(file_path, 'r') as file:
            original_code = file.read()

        # First try to compile the code
        compile_flag, compile_result = self.rust.rust_compile()
        
        if compile_flag == 1:  # Compilation failed
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
            with open(self.file_path, "w") as file:
                file.write(fixed_code)
            return 0, compile_result, fixed_code
            
        else:  # Compilation succeeded
            executable_path = file_path.rsplit('.', 1)[0]  # Remove .rs extension
            run_flag, run_result = self.rust.rust_run()
            
            if run_flag == 1:  # Runtime error
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
                with open(self.file_path, "w") as file:
                    file.write(fixed_code)
                return 1, run_result, fixed_code
                
            else:  # Everything succeeded
                print("run_result : ", run_result)
                return 0, run_result, None

# 使用示例
if __name__ == "__main__":
    modifier = RustCodeModifier(model="llama3.1", file_path="./rust_code.rs")
    modifier.modify("./rust_code.rs")

"""test Ollama Model"""
# model = "llama3.1"
# system_prompt_chat = """
# Chat with me
# You will generate the following JSON response:
# "response" : "your response to the given request"
# """
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
# if f == 1:
#     print("编译失败：")
# else:
#     print("编译成功：")
# print(type(res))
# print(res)

"""test modifier.rust_runner"""
# modifier = RustCodeModifier(model="llama3.1")
# f, res = modifier.rust_runner("./rust_code")
# if f == 1:
#     print("运行失败：")
# else:
#     print("运行成功：")
# print(type(res))
# print(res)

"""test modifier.modifier"""
# modifier = RustCodeModifier(model="llama3.1")
# f, res, code = modifier.modifier("./rust_code.rs")
# if(f == 0):
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