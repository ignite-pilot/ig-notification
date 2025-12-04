"""
Local 환경 설정
"""
from typing import Optional
import os


class LocalConfig:
    """Local 개발 환경 설정"""
    
    # Server Host
    HOST: str = "localhost"
    
    # Server Ports
    API_PORT: int = int(os.getenv("API_PORT", "8101"))
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8102"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8100"))
    
    # CORS 설정
    ALLOWED_ORIGINS: list = [
        "http://localhost:8100",
        "http://127.0.0.1:8100"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # API Security
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")  # 개발 환경은 DEBUG
    
    # Environment name
    ENV_NAME: str = "local"

