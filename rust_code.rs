use std::io;

fn main() {
    let mut n = String::new();
    io::stdin().read_line(&mut n).expect("Error reading input");
    let n: i32 = n.trim().parse().expect("Invalid input");
    let mut a = vec![0; 3030];

    for i in 1..=n {
        let mut num = String::new();
        io::stdin().read_line(&mut num).expect("Error reading input");
        let x: i32 = num.trim().parse().expect("Invalid input");
        a[i as usize] = x;
    }

    for i in 2..=n {
        a[1] &= a[i];
    }

    if a[1] == 0 {
        println!("Yes");
    } else {
        println!("No");
    }
}
