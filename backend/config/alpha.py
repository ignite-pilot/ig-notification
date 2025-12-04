"""
Alpha 환경 설정 (AWS Server)
"""
from typing import Optional
import os


class AlphaConfig:
    """Alpha 프로덕션 환경 설정"""
    
    # Server Host
    HOST: str = "alpha.ig-notification.ig-pilot.com"
    
    # Server Ports
    API_PORT: int = int(os.getenv("API_PORT", "8101"))
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8102"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8100"))
    
    # CORS 설정
    ALLOWED_ORIGINS: list = [
        "https://alpha.ig-notification.ig-pilot.com",
        "http://alpha.ig-notification.ig-pilot.com"  # HTTP도 허용 (필요시)
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # API Security (Alpha는 API 키 필수)
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # 프로덕션은 INFO
    
    # Environment name
    ENV_NAME: str = "alpha"

