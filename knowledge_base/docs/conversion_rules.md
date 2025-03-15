
# C++ → Rust 转换规则手册

## 目录
1. [基础语法转换](#一基础语法转换)  
2. [内存管理转换](#二内存管理转换)  
3. [面向对象转换](#三面向对象转换)  
4. [泛型与模板](#四泛型与模板)  
5. [标准库对应](#五标准库对应)  
6. [并发模型转换](#六并发模型转换)  
7. [错误处理转换](#七错误处理转换)  
8. [代码惯用法](#八代码惯用法)

---

## 一、基础语法转换

### 1.1 变量与常量
| C++ 模式                     | Rust 等效方式                     | 注意事项                          |
|------------------------------|-----------------------------------|-----------------------------------|
| `int x = 5;`                 | `let x: i32 = 5;`                | 默认不可变                        |
| `const int MAX = 100;`       | `const MAX: i32 = 100;`          | 必须显式标注类型                  |
| `constexpr int SIZE = 200;`  | `const SIZE: usize = 200;`       | 编译期计算                        |
| `auto y = 3.14;`             | `let y = 3.14_f64;`              | 推荐显式标注浮点类型              |

```cpp
// C++
const double PI = 3.14159;
auto name = "Rust";
```

```rust
// Rust
const PI: f64 = 3.14159;
let name: &str = "Rust";
```

---

## 二、内存管理转换

### 2.1 指针与智能指针
| C++ 模式                     | Rust 等效方式                     | 规则说明                          |
|------------------------------|-----------------------------------|-----------------------------------|
| `int* ptr = new int(5);`      | `let ptr = Box::new(5);`          | 所有权自动管理                    |
| `std::unique_ptr<int> uptr;` | `let uptr: Box<i32>;`             | 单一所有权                        |
| `std::shared_ptr<int> sptr;` | `let sptr: Arc<Mutex<i32>>;`      | 需要线程安全时使用                |
| `delete ptr;`                | 无需操作                         | 离开作用域自动释放                |

```cpp
// C++
auto p = std::make_unique<std::string>("hello");
```
```rust
// Rust
let p = Box::new(String::from("hello"));
```

### 2.2 移动语义
```cpp
// C++ 移动构造函数
Buffer(Buffer&& other) noexcept 
    : data(other.data), size(other.size) {
    other.data = nullptr;
}
```
```rust
// Rust 所有权转移
let s1 = String::from("hello");
let s2 = s1;  // s1 失效
```

---

## 三、面向对象转换

### 3.1 类与结构体
| C++ 模式                     | Rust 等效方式                     |
|------------------------------|-----------------------------------|
| `class MyClass { ... };`      | `struct MyClass { ... }`          |
| `class Derived : public Base`| `trait Base { ... }` + `impl Base for Derived` |
| `virtual void func() = 0;`   | `trait Method { fn func(&self); }`|

```cpp
// C++
class Animal {
public:
    virtual void sound() = 0;
};
```
```rust
// Rust
trait Animal {
    fn sound(&self);
}
```

### 3.2 多态实现
```cpp
// C++ 运行时多态
std::unique_ptr<Shape> shape = std::make_unique<Circle>(5.0);
```
```rust
// Rust trait对象
let shape: Box<dyn Shape> = Box::new(Circle { radius: 5.0 });
```

---

## 四、泛型与模板

### 4.1 函数模板
```cpp
// C++
template <typename T>
T max(T a, T b) { return a > b ? a : b; }
```
```rust
// Rust
fn max<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}
```

### 4.2 模板特化
```cpp
// C++
template <>
const char* max(const char* a, const char* b) {
    return strcmp(a, b) > 0 ? a : b;
}
```
```rust
// Rust 使用 trait 实现
impl PartialOrd for CStr {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
```

---

## 五、标准库对应

### 5.1 容器类
| C++ 容器                   | Rust 等效类型                  | 重要差异                          |
|---------------------------|-------------------------------|-----------------------------------|
| `std::vector<T>`          | `Vec<T>`                      | Rust 没有 capacity 保留空间概念   |
| `std::map<K,V>`           | `std::collections::HashMap<K,V>` | 默认无序                          |
| `std::unordered_set<T>`   | `HashSet<T>`                  | 需实现 Hash trait                 |
| `std::deque<T>`           | `VecDeque<T>`                 | 接口相似                          |

### 5.2 算法转换
```cpp
// C++ STL
std::sort(vec.begin(), vec.end());
```
```rust
// Rust
vec.sort();
```

---

## 六、并发模型转换

### 6.1 线程管理
```cpp
// C++
std::thread t([]{ /*...*/ });
t.join();
```
```rust
// Rust
let handle = thread::spawn(|| { /*...*/ });
handle.join().unwrap();
```

### 6.2 共享状态
```cpp
// C++ 互斥锁
std::mutex mtx;
std::lock_guard<std::mutex> lock(mtx);
```
```rust
// Rust
let counter = Arc::new(Mutex::new(0));
let mut num = counter.lock().unwrap();
```

---

## 七、错误处理转换

### 7.1 异常处理
```cpp
// C++
try {
    throw std::runtime_error("error");
} catch (const std::exception& e) {
    std::cerr << e.what();
}
```
```rust
// Rust
fn may_fail() -> Result<(), String> {
    Err("error".into())
}

if let Err(e) = may_fail() {
    eprintln!("{}", e);
}
```

### 7.2 错误传播
```cpp
// C++ 异常传播
void func() { throw MyError(); }
```
```rust
// Rust Result 传播
fn func() -> Result<(), MyError> {
    Err(MyError)?
}
```

---

## 八、代码惯用法

### 8.1 空指针处理
```cpp
// C++
if (ptr != nullptr) { /*...*/ }
```
```rust
// Rust
if let Some(val) = option_val {
    // 使用 val
}
```

### 8.2 资源管理
```cpp
// C++ RAII
class File {
    FILE* handle;
public:
    ~File() { fclose(handle); }
};
```
```rust
// Rust Drop trait
struct File {
    handle: std::fs::File,
}

impl Drop for File {
    fn drop(&mut self) {
        // 自动关闭文件
    }
}
```

---

> 版本：2024-06  
> 核心原则：  
> 1. C++ 手动管理 → Rust 所有权系统  
> 2. 继承 → Trait + 组合  
> 3. 异常 → Result/Option  
> 4. 模板 → 泛型 + Trait约束  
> 完整示例库：https://github.com/rust-lang/rust-by-example
```