import requests
import json
from typing import Dict, Optional, List
import time
import logging
import os
from datetime import datetime

class UnifiedLLMClient:
    def __init__(self):
        self.configs = {
            # 预定义的模型配置模板
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "headers": {
                    "Authorization": "Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                "endpoint": "/chat/completions",
                "prompt_field": "messages",
                "response_field": "choices[0].message.content"
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "headers": {
                    "Authorization": "Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                "endpoint": "/chat/completions",
                "prompt_field": "messages",
                "response_field": "choices[0].message.content"
            },
            # 在 UnifiedLLMClient 的 __init__ 方法中，修改 Ollama 的配置：
            "ollama": {
                "base_url": "http://localhost:11434",
                "headers": {
                    "Content-Type": "application/json"
                },
                "endpoint": "/api/generate",
                "prompt_field": "prompt",
                "response_field": "response",
                "params": {"stream": False}  # 添加默认参数
            }
        }
        self.active_models = {}  # 存储已配置的模型信息

        # 设置日志
        self._setup_logging()

    def _setup_logging(self):
        """配置日志系统"""
        # 创建 logs 目录
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # 生成日志文件名（包含时间戳）
        log_filename = f'logs/llm_client_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _format_json(self, data: Dict) -> str:
        """格式化 JSON 数据"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def add_model(
        self,
        model_name: str,
        config: Dict,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        添加或覆盖一个模型的配置
        :param model_name: 自定义模型名称（如 "my-gpt-4"）
        :param config: 模型配置模板（参考 self.configs 中的结构）
        :param api_key: 模型的 API 密钥（如果需要）
        :param model: 实际调用的模型名称（如 "gpt-4"）
        """
        # 替换模板中的占位符
        if api_key:
            config["headers"] = {
                k: v.format(api_key=api_key) for k, v in config["headers"].items()
            }
        self.active_models[model_name] = {
            "config": config,
            "model": model  # 实际调用的模型名称
        }
        self.logger.info(f"添加模型: {model_name}")
        self.logger.info(f"模型配置: \n{self._format_json(config)}")

    def generate(
        self,
        model_name: str,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        统一生成接口
        :param model_name: 已配置的模型名称
        :param prompt: 输入的提示文本
        :param max_tokens: 生成的最大 token 数量
        :param temperature: 温度参数
        :param kwargs: 模型特定的额外参数
        :return: 生成的文本
        """
        start_time = time.time()
        self.logger.info(f"\n{'='*50}\n开始生成回复...")
        self.logger.info(f"使用模型: {model_name}")

        if model_name not in self.active_models:
            raise ValueError(f"模型 {model_name} 未配置，请先调用 add_model()")

        model_config = self.active_models[model_name]
        config = model_config["config"]
        endpoint = f"{config['base_url']}{config['endpoint']}"

        # 构造请求数据
        data = {
            config['prompt_field']: prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "model": model_config.get("model"),
            **config.get("params", {}),
            **kwargs
        }
        
        # 记录请求信息
        self.logger.info(f"\n请求 URL: {endpoint}")
        self.logger.info(f"请求头: \n{self._format_json(config['headers'])}")
        self.logger.info(f"请求数据: \n{self._format_json(data)}")

        try:
            response = requests.post(
                endpoint,
                headers=config["headers"],
                json=data
            )
            response.raise_for_status()
            
            # 记录完整响应
            response_json = response.json()
            self.logger.info(f"响应数据: \n{self._format_json(response_json)}")
            
            result = self._extract_response(response_json, config['response_field'])
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"生成完成，耗时：{elapsed_time:.2f}秒")
            self.logger.info(f"生成结果: \n{result}\n{'='*50}\n")
            
            return result
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"请求失败，耗时：{elapsed_time:.2f}秒")
            self.logger.error(f"错误信息: {str(e)}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"错误响应: \n{self._format_json(e.response.json())}")
            raise RuntimeError(f"请求失败: {str(e)}")

    def _extract_response(self, response: Dict, field_path: str) -> str:
        """
        从嵌套的响应中提取目标字段
        :param response: API 返回的 JSON 数据
        :param field_path: 字段路径（如 "choices[0].message.content"）
        """
        keys = field_path.replace("[", ".").replace("]", "").split(".")
        result = response
        for key in keys:
            if isinstance(result, list):
                result = result[int(key)]
            else:
                result = result.get(key, "")
            if not result:
                return ""
        return result
    
