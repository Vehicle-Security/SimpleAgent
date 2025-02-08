import sys
sys.path.append("./agent")
sys.path.append("./demos/cpp2rust")
sys.path.append("./demos/cpp-compile-run")
sys.path.append("./demos/rust-compile-run")
from unified_llm_client import UnifiedLLMClient
from code_converter_agent import CodeConverterAgent
from code_modifier_agent import CodeModifierAgent


if __name__ == "__main__":
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )
    llm_client.add_model(
        model_name="deepseek-pro",
        config=llm_client.configs["deepseek"],
        api_key="sk-32351aabaf6547d290368eb33e45bd9f",
        model="deepseek-chat"
    )

    # converter = CodeConverterAgent(
    #     client=llm_client,
    #     model_name="ollama-llama3",
    #     input_path="./test_code/example.cpp",
    #     output_dir="./test_code/output",
    # )

    # modifier = CodeModifierAgent(
    #     client=llm_client,
    #     model_name="ollama-llama3",
    #     rust_path="./test_code/output/example.rs",
    #     cpp_path="./test_code/example.cpp"
    # )

    converter = CodeConverterAgent(
        client=llm_client,
        model_name="deepseek-pro",
        input_path="./test_code/example.cpp",
        output_dir="./test_code/output",
    )

    modifier = CodeModifierAgent(
        client=llm_client,
        model_name="deepseek-pro",
        rust_path="./test_code/output/example.rs",
        cpp_path="./test_code/example.cpp"
    )

    converter.convert()
    # converter.interactive_conversion()
    modifier.interactive_fixing()
