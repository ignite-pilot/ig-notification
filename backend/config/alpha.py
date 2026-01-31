"""
Alpha 환경 설정 (AWS Server)
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
            return [] if phase == "alpha" else ["http://localhost:8100"]
    except Exception as e:
        # 오류 발생 시 기본값 반환
        print(f"Warning: Failed to load CORS config: {e}")
        return [] if phase == "alpha" else ["http://localhost:8100"]


def load_database_url_from_aws() -> str:
    """AWS Secret Manager에서 MySQL 데이터베이스 정보를 가져와서 DATABASE_URL 구성"""
    try:
        # AWS 자격 증명은 환경 변수에서 가져오거나 IAM 역할 사용
        # ECS Task Definition의 secrets로 주입된 환경 변수 사용
        region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
        secrets_client = boto3.client('secretsmanager', region_name=region)
        response = secrets_client.get_secret_value(SecretId='prod/ignite-pilot/mysql-realpilot')
        secret = json.loads(response['SecretString'])
        
        db_host = secret.get('DB_HOST', '')
        db_port = secret.get('DB_PORT', '3306')  # MySQL 기본 포트
        db_user = secret.get('DB_USER', 'root')
        db_password = secret.get('DB_PASSWORD', '')
        # 프로젝트 이름으로 강제 설정 (Secret Manager의 DB_NAME 무시)
        db_name = 'ig-notification'
        
        # MySQL 연결 문자열 구성
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        return database_url
    except ClientError as e:
        print(f"Warning: Failed to load database config from AWS Secret Manager: {e}")
        return ""
    except Exception as e:
        print(f"Warning: Failed to load database config: {e}")
        return ""


class AlphaConfig:
    """Alpha 프로덕션 환경 설정"""
    
    # Server Host
    HOST: str = os.getenv("HOST", "ig-notification.ignite-pilot.com")
    
    # Server Ports
    API_PORT: int = int(os.getenv("API_PORT", "8101"))
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8102"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8100"))
    
    # CORS 설정 - 설정 파일에서 읽어오기
    ALLOWED_ORIGINS: list = load_cors_origins("alpha")
    
    # Database - AWS Secret Manager에서만 가져오기 (보안: 파일에 저장하지 않음)
    # 환경 변수 DATABASE_URL은 사용하지 않음 (보안상 파일에 저장하지 않음)
    DATABASE_URL: str = load_database_url_from_aws()
    
    # API Security (Alpha는 API 키 필수)
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # 프로덕션은 INFO
    
    # Environment name
    ENV_NAME: str = "alpha"

