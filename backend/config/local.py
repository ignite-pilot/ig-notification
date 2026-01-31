"""
Local 환경 설정
"""
from typing import Optional
import os
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError


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


def load_database_url_from_aws() -> str:
    """AWS Secret Manager에서 MySQL 데이터베이스 정보를 가져와서 DATABASE_URL 구성"""
    try:
        secrets_client = boto3.client('secretsmanager', region_name='ap-northeast-2')
        response = secrets_client.get_secret_value(SecretId='prod/ignite-pilot/mysql-realpilot')
        secret = json.loads(response['SecretString'])
        
        db_host = secret.get('DB_HOST', '')
        db_port = secret.get('DB_PORT', '3306')  # MySQL 기본 포트
        db_user = secret.get('DB_USER', 'root')
        db_password = secret.get('DB_PASSWORD', '')
        db_name = secret.get('DB_NAME', 'ig-notification')  # 프로젝트 이름으로 기본값 설정
        
        # MySQL 연결 문자열 구성
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        return database_url
    except ClientError as e:
        print(f"Warning: Failed to load database config from AWS Secret Manager: {e}")
        return ""
    except Exception as e:
        print(f"Warning: Failed to load database config: {e}")
        return ""


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
    
    # Database - 환경 변수 우선, 없으면 AWS Secret Manager에서 가져오기
    # 로컬 개발 환경에서는 환경 변수로 직접 설정 가능
    DATABASE_URL: str = os.getenv("DATABASE_URL", "") or load_database_url_from_aws()
    
    # API Security
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")  # 개발 환경은 DEBUG
    
    # Environment name
    ENV_NAME: str = "local"

