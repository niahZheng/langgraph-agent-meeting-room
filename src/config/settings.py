"""应用配置管理"""

import os
import warnings
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI


class Settings:
    """应用配置类"""
    
    # 环境变量加载
    def __init__(self):
        # 优先加载 .env，如果不存在则加载 env
        # 忽略解析错误，只显示警告
        env_loaded = False
        
        # 尝试加载 .env 文件
        if os.path.exists(".env"):
            try:
                # 使用 verbose=False 和 override=False 来静默处理错误
                result = load_dotenv(".env", override=False, verbose=False)
                if result:
                    env_loaded = True
            except Exception as e:
                # 如果 .env 解析失败，尝试修复或使用 env 文件
                warnings.warn(f".env 文件解析失败: {str(e)}，将尝试其他方式加载环境变量")
        
        # 如果 .env 不存在或解析失败，尝试 env 文件
        if not env_loaded and os.path.exists("env"):
            try:
                result = load_dotenv("env", override=False, verbose=False)
                if result:
                    env_loaded = True
            except Exception as e:
                # 如果都失败，继续使用系统环境变量
                warnings.warn(f"env 文件解析失败: {str(e)}，将使用系统环境变量")
        
        # 如果都没有，尝试默认加载（从当前目录查找）
        if not env_loaded:
            try:
                load_dotenv(override=False, verbose=False)
            except Exception:
                # 如果都失败，继续使用系统环境变量
                pass
    
    @property
    def dashscope_api_key(self) -> str:
        """通义千问 API Key"""
        key = os.getenv("DASHSCOPE_API_KEY")
        if not key:
            raise ValueError(
                "请设置 DASHSCOPE_API_KEY 环境变量或在 .env 文件中配置！\n"
                "注册地址：https://dashscope.aliyun.com/"
            )
        return key
    
    @property
    def model_name(self) -> str:
        """模型名称"""
        return os.getenv("MODEL_NAME", "qwen-plus")
    
    @property
    def base_url(self) -> str:
        """API Base URL"""
        return os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    @property
    def temperature(self) -> float:
        """模型温度参数"""
        return float(os.getenv("TEMPERATURE", "0.7"))
    
    @property
    def max_iterations(self) -> int:
        """最大迭代次数"""
        return int(os.getenv("MAX_ITERATIONS", "5"))


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


@st.cache_resource
def get_model() -> ChatOpenAI:
    """获取基础模型（使用缓存）
    
    Returns:
        ChatOpenAI 模型实例
    """
    settings = get_settings()
    
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.dashscope_api_key,
        base_url=settings.base_url,
        temperature=settings.temperature
    )

