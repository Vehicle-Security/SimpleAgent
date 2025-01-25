import subprocess

class Rust:
    def __init__(self, file_path):
        self.file_path = file_path
	
    def rust_compile(self):
        """
        Compile rust code

        Parameters:
        file_path(str)：需要编译的rust代码的path

        Rerturns:
        pair：
            success_flag(int)： 0 for success, 1 for failure
            result_message(str)：Compilation output or error message
        """
        file_path = self.file_path
        try:
            # 使用 subprocess 模块的 run 方法调用 bash 命令
            result = subprocess.run(['rustc', file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print("编译成功：", result.stdout.decode())
            return 0, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            # print("编译失败：", e.stderr.decode())
            return 1, e.stderr.decode()

    def rust_run(self):
        """
        Run executable file

        Parameters:
        file_path(str)：需要运行的rust代码的path

        Rerturns:
        pair：
            success_flag(int)： 0 for success, 1 for failure
            result_message(str)：Runtime output or error message
        """
        executable_path = self.file_path[:-3]  # 去掉 .rs 后缀，得到可执行文件的路径"
        print(executable_path)
        try:
            # 使用 subprocess 模块的 run 方法调用 bash 命令
            result = subprocess.run([executable_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print("运行成功：", result.stdout.decode())
            return 0, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            # print("运行失败：", e.stderr.decode())
            return 1, e.stderr.decode()
        

# compiler = Rust(file_path="../cpp2rust/rust_code.rs")
# compiler.rust_compile()
# compiler.rust_run()