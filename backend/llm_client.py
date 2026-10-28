"""
LLM客户端封装模块
统一管理与大模型API的交互，支持Mock模式方便测试
"""
from typing import Optional, Dict, Any
import json
import logging
from abc import ABC, abstractmethod

from config import get_settings

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用LLM生成内容
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            **kwargs: 额外参数如 temperature, max_tokens
        
        Returns:
            LLM返回的文本内容
        """
        pass
    
    def generate_with_json_output(
        self, 
        system_prompt: str, 
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        生成并确保输出为JSON格式
        
        子类可覆盖此方法以使用API原生的JSON模式
        """
        return self.generate(system_prompt, user_prompt, **kwargs)


class OpenAICompatibleClient(BaseLLMClient):
    """
    兼容OpenAI API的客户端
    支持DeepSeek、Qwen、Claude(通过兼容层)、GPT等
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ):
        settings = get_settings()
        self.api_key = api_key or settings.llm_api_key
        # 使用解析后的配置（支持国内模型预设自动填充）
        self.base_url = base_url or settings.resolved_base_url
        self.model = model or settings.resolved_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 延迟导入，避免没有openai包时模块无法加载
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self._available = True
        except ImportError:
            logger.warning("openai包未安装，OpenAICompatibleClient将不可用")
            self._available = False
            self.client = None
    
    def generate(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """调用LLM"""
        if not self._available:
            raise RuntimeError("OpenAI client不可用，请安装openai包")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                response_format={"type": "json_object"},  # 强制JSON输出
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM客户端
    用于测试和离线开发，返回预设的图数据
    """
    
    MOCK_RESPONSES = {
        "default": json.dumps({
            "diagram_type": "flowchart",
            "title": "用户登录流程",
            "nodes": [
                {"id": "start", "label": "开始", "type": "ellipse", "x": 400, "y": 50, "color": "#90EE90"},
                {"id": "input", "label": "输入账号密码", "type": "parallelogram", "x": 350, "y": 150},
                {"id": "check", "label": "验证信息?", "type": "diamond", "x": 380, "y": 250, "color": "#FFD6A5"},
                {"id": "success", "label": "登录成功", "type": "rectangle", "x": 100, "y": 350, "color": "#A8E6CF"},
                {"id": "fail", "label": "登录失败", "type": "rectangle", "x": 600, "y": 350, "color": "#FFB3BA"},
                {"id": "end", "label": "结束", "type": "ellipse", "x": 400, "y": 450, "color": "#90EE90"}
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "input", "arrow": "end"},
                {"id": "e2", "source": "input", "target": "check", "arrow": "end"},
                {"id": "e3", "source": "check", "target": "success", "label": "是", "arrow": "end"},
                {"id": "e4", "source": "check", "target": "fail", "label": "否", "arrow": "end"},
                {"id": "e5", "source": "success", "target": "end", "arrow": "end"},
                {"id": "e6", "source": "fail", "target": "end", "arrow": "end"}
            ]
        }, ensure_ascii=False),
        
        "architecture": json.dumps({
            "diagram_type": "architecture",
            "title": "Web系统架构",
            "nodes": [
                {"id": "client", "label": "客户端", "type": "rectangle", "x": 350, "y": 50, "color": "#95C2F6"},
                {"id": "nginx", "label": "Nginx", "type": "rectangle", "x": 380, "y": 150, "color": "#FDFD96"},
                {"id": "api", "label": "API网关", "type": "rectangle", "x": 370, "y": 250, "color": "#FFB5E8"},
                {"id": "service", "label": "微服务集群", "type": "rectangle", "x": 340, "y": 350, "color": "#B5DEFF"},
                {"id": "redis", "label": "Redis", "type": "cylinder", "x": 150, "y": 450, "color": "#FFD6A5"},
                {"id": "mysql", "label": "MySQL", "type": "cylinder", "x": 400, "y": 450, "color": "#CAFFBF"},
                {"id": "mq", "label": "消息队列", "type": "cloud", "x": 650, "y": 450, "color": "#E0BBE4"}
            ],
            "edges": [
                {"id": "e1", "source": "client", "target": "nginx"},
                {"id": "e2", "source": "nginx", "target": "api"},
                {"id": "e3", "source": "api", "target": "service"},
                {"id": "e4", "source": "service", "target": "redis"},
                {"id": "e5", "source": "service", "target": "mysql"},
                {"id": "e6", "source": "service", "target": "mq"}
            ]
        }, ensure_ascii=False)
    }
    
    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """返回预设的Mock数据"""
        # 根据用户输入关键词选择Mock响应
        prompt_lower = user_prompt.lower()
        
        if any(kw in prompt_lower for kw in ["架构", "architecture", "系统", "组件"]):
            return self.MOCK_RESPONSES["architecture"]
        
        return self.MOCK_RESPONSES["default"]


def create_llm_client(mock: bool = False) -> BaseLLMClient:
    """
    工厂函数：创建LLM客户端
    
    Args:
        mock: 是否使用Mock客户端
    
    Returns:
        LLM客户端实例
    """
    settings = get_settings()
    # 支持通过 MOCK_LLM 环境变量强制使用Mock模式（用于演示/测试，无需API Key）
    if mock or settings.mock_llm:
        logger.info("使用 Mock LLM 客户端（MOCK_LLM 已启用）")
        return MockLLMClient()
    
    try:
        client = OpenAICompatibleClient()
        if client._available:
            return client
        logger.warning("OpenAI客户端不可用，降级到Mock模式")
        return MockLLMClient()
    except Exception as e:
        logger.warning(f"创建OpenAI客户端失败，使用Mock模式: {e}")
        return MockLLMClient()
