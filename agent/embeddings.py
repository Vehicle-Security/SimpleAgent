import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingEngine:
    def __init__(self, model_name: str = None):
        """
        初始化embedding引擎，使用 TF-IDF 作为本地 embedding 方案
        """
        self.vectorizer = TfidfVectorizer()
        self.document_embeddings: Dict[str, np.ndarray] = {}
        self.documents: Dict[str, str] = {}
        self.fitted = False
    
    def add_document(self, doc_id: str, content: str, chunk_size: int = 512):
        """
        添加文档并生成embedding
        """
        # 存储文档
        self.documents[doc_id] = content
        
        # 如果已有文档，重新计算所有文档的 embeddings
        if self.documents:
            docs = list(self.documents.values())
            # 拟合并转换所有文档
            if not self.fitted:
                embeddings = self.vectorizer.fit_transform(docs)
                self.fitted = True
            else:
                embeddings = self.vectorizer.transform(docs)
            
            # 更新所有文档的 embeddings
            for idx, doc_id in enumerate(self.documents.keys()):
                self.document_embeddings[doc_id] = embeddings[idx]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        搜索相关文档
        """
        if not self.documents:
            return []
        
        # 将查询转换为向量
        query_vector = self.vectorizer.transform([query])
        
        results = []
        for doc_id, embedding in self.document_embeddings.items():
            # 计算相似度
            similarity = cosine_similarity(query_vector, embedding)[0][0]
            results.append({
                'doc_id': doc_id,
                'content': self.documents[doc_id],
                'score': float(similarity)
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k] 