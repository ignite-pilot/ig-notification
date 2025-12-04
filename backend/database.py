from sqlalchemy import create_engine, Column, String, Integer, BigInteger, DateTime, Text, ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from datetime import datetime
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_email = Column(String(255), nullable=False)
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

