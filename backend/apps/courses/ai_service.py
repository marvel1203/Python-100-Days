"""
AI服务集成
支持Ollama本地/远程、DeepSeek、OpenAI等多种AI服务
"""
import requests
import json
from typing import List, Dict, Optional


class AIService:
    """AI服务基类"""
    
    def __init__(self, config):
        self.config = config
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送聊天消息"""
        raise NotImplementedError


class OllamaService(AIService):
    """Ollama服务"""
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        调用Ollama API
        :param messages: 消息列表 [{'role': 'user', 'content': '...'}]
        :return: AI响应内容
        """
        url = f"{self.config.api_endpoint}/api/chat"
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get('message', {}).get('content', '')
        
        except requests.RequestException as e:
            raise Exception(f"Ollama API调用失败: {str(e)}")


class DeepSeekService(AIService):
    """DeepSeek服务"""
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        调用DeepSeek API
        :param messages: 消息列表
        :return: AI响应内容
        """
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model_name or "deepseek-chat",
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except requests.RequestException as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")


class OpenAIService(AIService):
    """OpenAI服务"""
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        调用OpenAI API
        :param messages: 消息列表
        :return: AI响应内容
        """
        url = f"{self.config.api_endpoint or 'https://api.openai.com'}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model_name or "gpt-3.5-turbo",
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except requests.RequestException as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")


class AIServiceFactory:
    """AI服务工厂"""
    
    @staticmethod
    def create(config) -> AIService:
        """
        根据配置创建AI服务实例
        :param config: AIConfig模型实例
        :return: AIService实例
        """
        service_map = {
            'ollama_local': OllamaService,
            'ollama_remote': OllamaService,
            'deepseek': DeepSeekService,
            'openai': OpenAIService,
        }
        
        service_class = service_map.get(config.provider)
        if not service_class:
            raise ValueError(f"不支持的AI服务提供商: {config.provider}")
        
        return service_class(config)
