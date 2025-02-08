from unified_llm_client import UnifiedLLMClient
from ai_agent import AIAgent

# 初始化统一客户端
llm_client = UnifiedLLMClient()

# 配置DeepSeek模型（需要替换真实API密钥）
DEEPSEEK_API_KEY = "sk-32351aabaf6547d290368eb33e45bd9f"
llm_client.add_model(
    model_name="deepseek-pro",
    config=llm_client.configs["deepseek"],  # 使用预定义的deepseek配置模板
    api_key=DEEPSEEK_API_KEY,
    model="deepseek-chat"  # 实际调用的模型名称
)

# 创建历史专家AI助手
system_prompt = """你是一位中国历史专家，请遵循以下要求：
1. 回答需准确引用史料记载
2. 重要事件需注明出处文献
3. 使用中文文言文与白话文混合风格"""

history_agent = AIAgent(
    client=llm_client,
    system_prompt=system_prompt,
    model_name="deepseek-pro",
    max_history=3  # 保留最近3轮对话
)

# 进行多轮对话测试
queries = [
    "简述秦始皇统一六国的过程",
    "详细说明书同文政策的具体措施",
    "这些改革对后世有什么影响？"
]

for idx, query in enumerate(queries, 1):
    print(f"\n[第{idx}轮对话]")
    print("用户:", query)
    response = history_agent.chat(
        query,
        temperature=0.3,  # 降低随机性
        max_tokens=400
    )
    print("AI:", response)
    print("-" * 50)

# 验证历史上下文保留
print("\n当前对话历史：")
for msg in history_agent.message_history[-4:]:  # 显示最后两轮对话
    print(f"{msg['role'].upper()}: {msg['content'][:60]}...")