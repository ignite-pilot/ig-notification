from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    # 환경 변수에서 읽기 (하드코딩 제거)
    database_url: str = os.getenv("DATABASE_URL", "")
    api_port: int = int(os.getenv("API_PORT", "8101"))
    mcp_port: int = int(os.getenv("MCP_PORT", "8102"))
    api_key: Optional[str] = os.getenv("API_KEY", None)  # API 인증용 키
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:8100")  # CORS 허용 도메인 (쉼표로 구분)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")  # 로깅 레벨
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    @property
    def allowed_origins_list(self) -> list:
        """CORS 허용 도메인 리스트 반환"""
        if not self.allowed_origins:
            return ["http://localhost:8100"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()

