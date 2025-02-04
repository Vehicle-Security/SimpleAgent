import subprocess

class Cpp:
    def __init__(self, file_path):
        self.file_path = file_path

    def cpp_compile(self):
        """
        Compile C++ code

        Parameters:
        file_path(str): 需要编译的C++代码的路径

        Returns:
        pair:
            success_flag(int): 0 for success, 1 for failure
            result_message(str): 编译输出或错误信息
        """
        file_path = self.file_path
        executable_path = file_path[:-4]  # 去掉 .cpp 后缀，得到可执行文件的路径
        try:
            # 使用 subprocess 模块的 run 方法调用 g++ 编译命令
            result = subprocess.run(['g++', file_path, '-o', executable_path], 
                                 check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return 0, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return 1, e.stderr.decode()

    def cpp_run(self):
        """
        Run executable file

        Parameters:
        file_path(str): 需要运行的C++代码的路径

        Returns:
        pair:
            success_flag(int): 0 for success, 1 for failure
            result_message(str): 运行时输出或错误信息
        """
        executable_path = self.file_path[:-4]  # 去掉 .cpp 后缀，得到可执行文件的路径
        try:
            # 使用 subprocess 模块的 run 方法调用可执行文件
            result = subprocess.run([executable_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print("运行成功：", result.stdout.decode())
            return 0, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            # print("运行失败：", e.stderr.decode())
            return 1, e.stderr.decode()

# 使用示例
if __name__ == '__main__':
    cpp_file = '../cpp2rust/c_code.cpp'  # 替换为你的C++文件路径
    cpp = Cpp(cpp_file)

    # 编译C++代码
    compile_flag, compile_output = cpp.cpp_compile()
    if compile_flag == 0:
        print("编译成功！")
        print(compile_output)

        # 运行编译后的可执行文件
        run_flag, run_output = cpp.cpp_run()
        if run_flag == 0:
            print("运行成功！")
            print(run_output)
        else:
            print("运行失败！")
            print(run_output)
    else:
        print("编译失败！")
        print(compile_output)