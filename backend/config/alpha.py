"""
Alpha 환경 설정 (AWS Server)
"""
from typing import Optional
import os
import json
from pathlib import Path


def load_cors_origins(phase: str) -> list:
    """CORS 허용 도메인을 설정 파일에서 읽어오기"""
    config_dir = Path(__file__).parent
    cors_config_file = config_dir / "cors_allowed_origins.json"
    
    try:
        if cors_config_file.exists():
            with open(cors_config_file, 'r', encoding='utf-8') as f:
                cors_config = json.load(f)
                return cors_config.get(phase, [])
        else:
            # 설정 파일이 없으면 기본값 반환
            return [] if phase == "alpha" else ["http://localhost:8100"]
    except Exception as e:
        # 오류 발생 시 기본값 반환
        print(f"Warning: Failed to load CORS config: {e}")
        return [] if phase == "alpha" else ["http://localhost:8100"]


class AlphaConfig:
    """Alpha 프로덕션 환경 설정"""
    
    # Server Host
    HOST: str = "alpha.ig-notification.ig-pilot.com"
    
    # Server Ports
    API_PORT: int = int(os.getenv("API_PORT", "8101"))
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8102"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8100"))
    
    # CORS 설정 - 설정 파일에서 읽어오기
    ALLOWED_ORIGINS: list = load_cors_origins("alpha")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # API Security (Alpha는 API 키 필수)
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # 프로덕션은 INFO
    
    # Environment name
    ENV_NAME: str = "alpha"

