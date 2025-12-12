"""
Local 환경 설정
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
            return ["http://localhost:8100"] if phase == "local" else []
    except Exception as e:
        # 오류 발생 시 기본값 반환
        print(f"Warning: Failed to load CORS config: {e}")
        return ["http://localhost:8100"] if phase == "local" else []


class LocalConfig:
    """Local 개발 환경 설정"""
    
    # Server Host
    HOST: str = "localhost"
    
    # Server Ports
    API_PORT: int = int(os.getenv("API_PORT", "8101"))
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8102"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8100"))
    
    # CORS 설정 - 통합 서버이므로 같은 origin에서 서빙
    # 외부 API 호출을 위한 CORS는 설정 파일에서 읽어오기
    ALLOWED_ORIGINS: list = load_cors_origins("local")
    # 통합 서버이므로 localhost도 추가
    if "http://localhost:8101" not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append("http://localhost:8101")
    if "http://127.0.0.1:8101" not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append("http://127.0.0.1:8101")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # API Security
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")  # 개발 환경은 DEBUG
    
    # Environment name
    ENV_NAME: str = "local"

