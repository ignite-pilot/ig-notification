from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:vmcMrs75!KZHk2johkRR:]wL@aidev-pgvector-dev.crkgaskg6o61.ap-northeast-2.rds.amazonaws.com:5432/ig-notification"
    api_port: int = 8002
    mcp_port: int = 8003
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

