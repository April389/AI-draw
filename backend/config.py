"""
应用配置模块
从环境变量或.env文件读取配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # LLM配置 - 支持OpenAI API格式的任何大模型服务
    llm_api_key: str = "sk-demo-key-change-me"
    llm_base_url: str = "https://api.deepseek.com/v1"  # 默认使用DeepSeek，可替换
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096
    
    # 服务配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # CORS
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取单例配置实例"""
    return Settings()
