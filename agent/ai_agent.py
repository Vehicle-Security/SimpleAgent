from unified_llm_client import UnifiedLLMClient
from typing import Dict, Optional, List

class AIAgent:
    def __init__(
        self,
        client: UnifiedLLMClient,
        system_prompt: str,
        model_name: str,
        max_history: int = 5  # 保留最近的对话轮次
    ):
        """
        初始化 AI Agent
        :param client: 配置好的 UnifiedLLMClient 实例
        :param system_prompt: 系统角色设定（例如 "你是一个幽默的助手"）
        :param model_name: UnifiedLLMClient 中已配置的模型名称（如 "gpt-4"）
        :param max_history: 保留的对话历史长度（防止上下文过长）
        """
        self.client = client
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.max_history = max_history
        self.message_history: List[Dict] = []

        # 初始化时添加系统提示
        self._add_system_prompt()

    def _add_system_prompt(self):
        """将系统提示添加到消息历史中（根据模型类型调整格式）"""
        # 根据模型类型决定如何包装系统提示
        model_type = self.client.active_models[self.model_name]["config"].get("type", "general")
        model_config = self.client.active_models[self.model_name]["config"]
        if model_config.get("prompt_field") == "messages":
            self.message_history.append({
                "role": "system", 
                "content": self.system_prompt
            })
        elif model_type == "openai":
            # OpenAI 风格的 system 角色
            self.message_history.append({
                "role": "user",
                "content": f"System Prompt: {self.system_prompt}"
            })
        else:
            # 通用方式：将系统提示作为第一条用户消息
            self.message_history.append({
                "role": "user",
                "content": f"System Prompt: {self.system_prompt}"
            })

    def chat(self, user_input: str, **kwargs) -> str:
        """
        执行一次对话
        :param user_input: 用户输入文本
        :param kwargs: 传递给 UnifiedLLMClient.generate() 的额外参数
        :return: 模型生成的回复
        """
        # 添加用户输入到历史
        self.message_history.append({
            "role": "user",
            "content": user_input
        })

        # 构造模型所需的 prompt（根据模型类型适配）
        model_config = self.client.active_models[self.model_name]["config"]
        if model_config.get("prompt_field") == "messages":
            # OpenAI 风格：直接使用消息历史
            prompt = self.message_history
        else:
            # 通用模型：拼接历史对话为字符串
            formatted = self._format_history_to_text()
            # 在提示的最后添加"不要写出多余的思考步骤"
            prompt = f"{formatted}\n不要写出多余的思考步骤"

        # 调用模型生成回复
        response = self.client.generate(
            model_name=self.model_name,
            prompt=prompt,
            **kwargs
        )

        # 添加模型回复到历史
        self.message_history.append({
            "role": "assistant",
            "content": response
        })

        # 限制历史长度
        if len(self.message_history) > self.max_history * 2:  # 保留 max_history 轮对话
            self.message_history = self.message_history[-self.max_history * 2:]

        return response

    def _format_history_to_text(self) -> str:
        """将消息历史格式化为纯文本（适用于非 message 格式的模型）"""
        formatted = []
        for msg in self.message_history:
            if msg["role"] == "system":
                formatted.append(f"System: {msg['content']}")
            else:
                formatted.append(f"{msg['role'].capitalize()}: {msg['content']}")
        return "\n".join(formatted)

    def reset(self):
        """重置对话历史（保留系统提示）"""
        self.message_history = []
        self._add_system_prompt()

# ===== 使用示例 =====
if __name__ == "__main__":
    # 1. 初始化 UnifiedLLMClient 并配置模型
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )

    # 2. 创建 AI Agent
    system_prompt = "你是一个精通中国历史的AI助手，回答时请引用真实历史事件。"
    agent = AIAgent(
        client=llm_client,
        system_prompt=system_prompt,
        model_name="ollama-llama3"
    )

    # 3. 进行对话
    user_query = "请讲述明朝永乐年间的郑和下西洋"
    response = agent.chat(user_query, max_tokens=300)
    print("用户:", user_query)
    print("AI:", response)

    # 4. 继续对话（保留上下文）
    follow_up = "当时的主要船只叫什么名字？"
    response = agent.chat(follow_up)
    print("\n用户:", follow_up)
    print("AI:", response)