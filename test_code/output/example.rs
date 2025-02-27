use std::io;

fn main() {
    let mut n = String::new();
    io::stdin().read_line(&mut n).expect("Failed to read line");
    let n: i32 = match n.trim().parse() {
        Ok(num) => num,
        Err(_) => panic!("Invalid input"),
    };
    println!("n = {}", n);
}