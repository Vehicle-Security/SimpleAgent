from ai_agent import AIAgent
from unified_llm_client import UnifiedLLMClient
from embeddings import EmbeddingEngine
from typing import List, Dict, Optional
import os

class RAGAgent(AIAgent):
    def __init__(
        self,
        client: UnifiedLLMClient,
        model_name: str,
        knowledge_base_path: str,
        embedding_model: str = "all-MiniLM-L6-v2",
        system_prompt: Optional[str] = None,
        max_history: int = 5
    ):
        """
        初始化 RAG Agent
        :param embedding_model: 使用的embedding模型名称
        """
        default_system_prompt = (
            "你是一个基于知识库的智能助手。请基于提供的相关文档回答问题，"
            "如果知识库中没有相关信息，请明确说明。\n\n"
            "请严格按照以下JSON格式响应：\n"
            "{\n"
            "    \"answer\": \"回答内容\",\n"
            "    \"source\": \"使用的知识来源\",\n"
            "    \"confidence\": \"回答的确信度（高/中/低）\"\n"
            "}\n"
            "不要写出多余的思考步骤"
        )
        
        super().__init__(
            client=client,
            system_prompt=system_prompt or default_system_prompt,
            model_name=model_name,
            max_history=max_history
        )
        
        self.knowledge_base_path = knowledge_base_path
        self.embedding_engine = EmbeddingEngine(embedding_model)
        self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self):
        """初始化知识库并生成embeddings"""
        for root, _, files in os.walk(self.knowledge_base_path):
            for file in files:
                if file.endswith(('.md', '.txt')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.embedding_engine.add_document(file_path, content)
    
    def _search_relevant_docs(self, query: str, top_k: int = 2) -> List[Dict]:
        """使用embedding搜索相关文档"""
        return self.embedding_engine.search(query, top_k)
    
    def chat(self, user_input: str, **kwargs) -> str:
        """增强的对话函数，使用embedding检索"""
        # 检索相关文档
        relevant_docs = self._search_relevant_docs(user_input)
        
        # 构建增强的提示
        context_docs = []
        for doc in relevant_docs:
            context_docs.append(
                f"参考文档 ({os.path.basename(doc['doc_id'])}):\n{doc['content']}\n"
            )
        
        enhanced_prompt = (
            "参考资料：\n"
            f"{''.join(context_docs)}\n"
            f"用户请求：{user_input}\n\n"
            "请基于以上参考资料回答，并严格按照指定的JSON格式响应。"
        )
        
        return super().chat(enhanced_prompt, **kwargs)

# 使用示例
if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = UnifiedLLMClient()
    llm_client.add_model(
        model_name="ollama-llama3",
        config=llm_client.configs["ollama"],
        model="llama3.1"
    )
    
    # 创建RAG Agent
    rag_agent = RAGAgent(
        client=llm_client,
        model_name="ollama-llama3",
        knowledge_base_path="./knowledge_base"
    )
    
    # 测试对话
    response = rag_agent.chat("如何将C++代码转换为Rust代码？")
    print(response) 