use std::io;

fn main() {
    let mut n = String::new(); // 添加一个变量声明和初始化
    io::stdin().read_line(&mut n).expect("Failed to read line"); // 使用标准输入读取值
    let n: i32 = n.trim().parse().expect("Please type a number!"); // 解析字符串为整数
    println!("n = {}", n); // 输出变量值
}