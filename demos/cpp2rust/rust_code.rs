use std::io;
const MAXN: usize = 3030;
fn main() {
    let mut n = String::new();
    io::stdin().read_line(&mut n).unwrap();
    let n: u32 = n.trim().parse().unwrap();
    let mut a = vec![0; MAXN];
    for i in 1..=n {
        let mut temp = String::new();
        io::stdin().read_line(&mut temp).unwrap();
        a[i] = temp.trim().parse::<u32>().unwrap();
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
}