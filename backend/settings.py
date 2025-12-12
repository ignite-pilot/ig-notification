"""
Phase별 설정을 사용하는 Settings 클래스
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Phase별 설정 import (순환 import 방지를 위해 여기서 import)
from config import phase_config


class Settings(BaseSettings):
    """Phase별 설정을 사용하는 Settings"""
    
    # Phase별 설정에서 가져오기
    database_url: str = phase_config.DATABASE_URL
    api_port: int = phase_config.API_PORT
    mcp_port: int = phase_config.MCP_PORT
    api_key: Optional[str] = phase_config.API_KEY
    allowed_origins_list: list = phase_config.ALLOWED_ORIGINS
    log_level: str = phase_config.LOG_LEVEL
    host: str = phase_config.HOST
    env_name: str = phase_config.ENV_NAME
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()

