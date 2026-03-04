from sqlalchemy import create_engine, Column, String, Integer, BigInteger, DateTime, Text, CHAR
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.mysql import JSON
import uuid
from datetime import datetime
from settings import settings

# Connection pool 설정으로 MySQL "server has gone away" 에러 방지
# - pool_recycle: 연결을 주기적으로 재생성 (MySQL wait_timeout보다 짧게 설정)
# - pool_pre_ping: 연결 사용 전 유효성 확인 (끊어진 연결 자동 감지 및 재연결)
# - connect_args: MySQL 연결 타임아웃 설정
engine = create_engine(
    settings.database_url,
    pool_recycle=3600,  # 1시간마다 연결 재생성 (MySQL wait_timeout보다 짧게)
    pool_pre_ping=True,  # 연결 사용 전 ping으로 유효성 확인
    pool_size=5,  # 기본 연결 풀 크기
    max_overflow=10,  # 추가 연결 허용
    connect_args={
        "connect_timeout": 10,  # 연결 타임아웃 10초
        "read_timeout": 30,  # 읽기 타임아웃 30초
        "write_timeout": 30,  # 쓰기 타임아웃 30초
        "autocommit": False,  # SQLAlchemy가 트랜잭션 관리
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EmailLog(Base):
    __tablename__ = "email_logs"
    
    # MySQL: UUID를 CHAR(36)로 저장 (UUID 타입 대신)
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_email = Column(String(255), nullable=False)
    # MySQL: JSON 타입 사용 (MySQL 5.7.8+)
    recipient_emails = Column(JSON, nullable=False)  # List of strings
    cc_emails = Column(JSON, nullable=True)  # List of strings
    bcc_emails = Column(JSON, nullable=True)  # List of strings
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    use_ssl = Column(String(10), default="true")
    status = Column(String(50), default="pending")  # pending, success, failed
    error_message = Column(Text, nullable=True)
    attachment_count = Column(Integer, default=0)
    total_attachment_size = Column(BigInteger, default=0)  # bytes
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

