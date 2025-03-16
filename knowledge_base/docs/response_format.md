# AI响应格式规范

## 工具选择响应示例
```json
{
    "tool": "converter",
    "reason": "用户明确要求将C++代码转换为Rust代码",
    "action": "使用converter工具进行代码转换，并生成对应的Cargo.toml文件"
}
```

## 代码转换响应示例
```json
{
    "rust_code": "fn main() {\n    println!(\"Hello, World!\");\n}",
    "cargo_toml": "[package]\nname = \"example\"\nversion = \"0.1.0\"\n",
    "explanation": "转换了基本的打印功能，使用Rust的println!宏替代C++的cout"
}
```

## 代码修正响应示例
```json
{
    "analysis": "发现编译错误：变量类型不匹配",
    "modified_code": "let x: i32 = 42;",
    "changes": "添加了明确的类型标注"
}
```
```

4. 修改 `unified_llm_client.py` 中的生成参数，增加格式控制：

```python:agent/unified_llm_client.py
def generate(self, model_name: str, prompt: str, **kwargs):
    # ... 现有代码 ...
    data = {
        config['prompt_field']: (
            f"{prompt}\n\n"
            "注意：你必须使用有效的JSON格式响应，"
            "不要包含任何其他格式的内容。"
        ),
        "max_tokens": max_tokens,
        "temperature": temperature,
        "model": model_config.get("model"),
        **config.get("params", {}),
        **kwargs
    }
    # ... 其余代码 ...
```

这些修改的目的是：
1. 在多个层面强调 JSON 格式要求
2. 确保 RAG 检索的内容不会干扰响应格式
3. 提供更明确的格式示例
4. 在提示中添加格式验证提醒

这样应该能够帮助 LLM 更好地理解和遵循我们期望的 JSON 响应格式。你想要我详细解释某个部分吗？