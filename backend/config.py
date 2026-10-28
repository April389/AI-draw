"""
应用配置模块
从环境变量或.env文件读取配置

默认使用国内大模型（通义千问 Qwen / DeepSeek），
两者均兼容 OpenAI API 格式，无需切换 SDK。
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal


# 国内大模型预设配置
# 通义千问（Qwen）和 DeepSeek 均提供 OpenAI 兼容接口
LLM_PROVIDER_PRESETS = {
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "description": "通义千问 Qwen-Plus（阿里云 DashScope）"
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "description": "DeepSeek Chat"
    },
    "qwen-turbo": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo",
        "description": "通义千问 Qwen-Turbo（更快更便宜）"
    },
    "deepseek-reasoner": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-reasoner",
        "description": "DeepSeek R1 推理模型"
    },
}


class Settings(BaseSettings):
    """应用配置类"""

    # ==================== LLM 配置 ====================
    # 国内模型提供商预设：qwen / deepseek / qwen-turbo / deepseek-reasoner / custom
    # 选择预设后会自动填充 base_url 和 model（除非显式覆盖）
    llm_provider: Literal["qwen", "deepseek", "qwen-turbo", "deepseek-reasoner", "custom"] = "qwen"

    # API Key（必填，国内模型需到对应控制台申请）
    # 通义千问: https://dashscope.console.aliyun.com/
    # DeepSeek: https://platform.deepseek.com/
    llm_api_key: str = "sk-your-api-key-here"

    # Mock 模式：设为 true 时使用预设图数据，无需 API Key（适合离线演示/测试）
    mock_llm: bool = False

    # 以下两项在选择预设时自动填充，设置 llm_provider=custom 时需手动填写
    llm_base_url: str = ""
    llm_model: str = ""

    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096

    # ==================== 服务配置 ====================
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # CORS
    cors_origins: str = "*"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

    @property
    def resolved_base_url(self) -> str:
        """解析后的 API Base URL（优先使用显式配置，否则取预设）"""
        if self.llm_base_url:
            return self.llm_base_url
        preset = LLM_PROVIDER_PRESETS.get(self.llm_provider)
        return preset["base_url"] if preset else ""

    @property
    def resolved_model(self) -> str:
        """解析后的模型名称（优先使用显式配置，否则取预设）"""
        if self.llm_model:
            return self.llm_model
        preset = LLM_PROVIDER_PRESETS.get(self.llm_provider)
        return preset["model"] if preset else ""

    @property
    def provider_description(self) -> str:
        """当前模型提供商描述"""
        preset = LLM_PROVIDER_PRESETS.get(self.llm_provider)
        return preset["description"] if preset else "自定义模型"


@lru_cache()
def get_settings() -> Settings:
    """获取单例配置实例"""
    return Settings()
