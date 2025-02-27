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

    def cpp_run(self, input_file=None):
        """
        Run executable file

        Parameters:
        input_file(str): Optional input file path for the C++ program
        
        Returns:
        pair:
            success_flag(int): 0 for success, 1 for failure
            result_message(str): 运行时输出或错误信息
        """
        executable_path = self.file_path[:-4]  # 去掉 .cpp 后缀，得到可执行文件的路径
        try:
            if input_file:
                # 如果提供了输入文件，从文件重定向输入
                with open(input_file, 'r') as f:
                    result = subprocess.run([executable_path], 
                                         input=f.read().encode(),
                                         check=True, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
            else:
                # 原有的运行方式
                result = subprocess.run([executable_path], 
                                     check=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            return 0, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return 1, e.stderr.decode()
        except FileNotFoundError as e:
            return 1, f"Input file not found: {input_file}"

# 使用示例
if __name__ == '__main__':
    cpp_file = '../../test_code/example.cpp'  # 替换为你的C++文件路径
    input_file = '../../test_code/input'  # 替换为你的输入文件路径
    cpp = Cpp(cpp_file)

    # 编译C++代码
    compile_flag, compile_output = cpp.cpp_compile()
    if compile_flag == 0:
        print("编译成功！")
        print(compile_output)

        # 运行编译后的可执行文件（带输入文件）
        run_flag, run_output = cpp.cpp_run(input_file)
        if run_flag == 0:
            print("运行成功！")
            print(run_output)
        else:
            print("运行失败！")
            print(run_output)
    else:
        print("编译失败！")
        print(compile_output)