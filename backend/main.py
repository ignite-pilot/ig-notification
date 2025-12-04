from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import logging
import os

from database import get_db, init_db, EmailLog
from models import EmailSendRequest, EmailSendResponse, EmailLogResponse
from email_service import EmailService
from config import settings

# 로깅 레벨을 환경 변수에서 읽기
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed: {str(e)}. Server will continue without database.")
    yield
    # Shutdown (필요한 경우 정리 작업)

app = FastAPI(title="IG Notification API", version="1.0.0", lifespan=lifespan)

# Rate Limiting 설정
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정 - 환경 변수에서 허용 도메인 읽기
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# API 키 인증 (선택적 - API_KEY가 설정된 경우에만 활성화)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """API 키 검증 (API_KEY가 설정된 경우에만 활성화)"""
    if settings.api_key:
        if not x_api_key or x_api_key != settings.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key. Please provide a valid X-API-Key header."
            )
    return x_api_key


@app.post("/api/v1/email/send", response_model=EmailSendResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")  # Rate limiting: 분당 10회 제한
async def send_email(
    request: Request,
    recipient_emails: str = Form(...),  # JSON string
    sender_email: str = Form(...),
    smtp_host: str = Form(...),
    smtp_port: int = Form(...),
    smtp_username: Optional[str] = Form(None),
    smtp_password: Optional[str] = Form(None),
    use_ssl: bool = Form(True),
    verify_ssl: bool = Form(True),  # SSL 인증서 검증 여부
    cc_emails: Optional[str] = Form(None),  # JSON string
    bcc_emails: Optional[str] = Form(None),  # JSON string
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """
    이메일 발송 API
    """
    import json
    from email_validator import validate_email, EmailNotValidError
    
    try:
        # Parse JSON strings
        recipient_list = json.loads(recipient_emails)
        cc_list = json.loads(cc_emails) if cc_emails else None
        bcc_list = json.loads(bcc_emails) if bcc_emails else None
        
        # Validate recipients
        if len(recipient_list) > 100:
            raise HTTPException(status_code=400, detail="최대 100명까지 발송 가능합니다.")
        if len(recipient_list) == 0:
            raise HTTPException(status_code=400, detail="받는 사람 이메일을 최소 1개 이상 입력해주세요.")
        
        # 이메일 형식 검증
        def validate_email_list(emails: List[str], field_name: str = "이메일"):
            for email in emails:
                try:
                    validate_email(email)
                except EmailNotValidError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"유효하지 않은 {field_name} 주소: {email}"
                    )
        
        validate_email_list(recipient_list, "받는 사람")
        validate_email_list([sender_email], "보내는 사람")
        if cc_list:
            validate_email_list(cc_list, "참조")
        if bcc_list:
            validate_email_list(bcc_list, "숨은 참조")
        
        # Process attachments with security validation
        attachments = []
        total_size = 0
        ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.xls', '.xlsx', '.csv'}
        ALLOWED_MIME_TYPES = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv',
            'image/jpeg',
            'image/png',
            'image/gif'
        }
        
        if files:
            if len(files) > 10:
                raise HTTPException(status_code=400, detail="첨부파일은 최대 10개까지 가능합니다.")
            
            for file in files:
                # 파일명 검증
                if not file.filename:
                    raise HTTPException(status_code=400, detail="파일명이 없습니다.")
                
                # 확장자 검증
                file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                if file_ext not in ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"허용되지 않은 파일 형식입니다. 허용 형식: {', '.join(ALLOWED_EXTENSIONS)}"
                    )
                
                # MIME 타입 검증
                content_type = file.content_type
                if content_type and content_type not in ALLOWED_MIME_TYPES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"허용되지 않은 파일 타입입니다."
                    )
                
                content = await file.read()
                total_size += len(content)
                
                if total_size > 30 * 1024 * 1024:  # 30MB
                    raise HTTPException(status_code=400, detail="첨부파일 총 크기는 30MB를 넘을 수 없습니다.")
                
                attachments.append({
                    'filename': file.filename,
                    'content': base64.b64encode(content).decode('utf-8')
                })
        
        # Create email log
        email_log = EmailLog(
            sender_email=sender_email,
            recipient_emails=recipient_list,
            cc_emails=cc_list,
            bcc_emails=bcc_list,
            subject=subject,
            body=body,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            use_ssl="true" if use_ssl else "false",
            status="pending",
            attachment_count=len(attachments),
            total_attachment_size=total_size
        )
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        
        # Send email
        success, error_message = await EmailService.send_email(
            recipient_emails=recipient_list,
            sender_email=sender_email,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            use_ssl=use_ssl,
            subject=subject,
            body=body,
            cc_emails=cc_list,
            bcc_emails=bcc_list,
            attachments=attachments if attachments else None,
            verify_ssl=verify_ssl
        )
        
        # Update log
        if success:
            email_log.status = "success"
            email_log.sent_at = datetime.utcnow()
        else:
            email_log.status = "failed"
            email_log.error_message = error_message
        
        db.commit()
        
        return EmailSendResponse(
            log_id=email_log.id,
            status=email_log.status,
            message="이메일이 성공적으로 발송되었습니다." if success else f"이메일 발송 실패: {error_message}",
            created_at=email_log.created_at
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다.")
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except Exception as e:
        logger.error(f"이메일 발송 중 오류: {str(e)}")
        # 프로덕션에서는 상세 에러를 숨김
        raise HTTPException(
            status_code=500,
            detail="서버 오류가 발생했습니다. 관리자에게 문의하세요."
        )


@app.get("/api/v1/email/logs", response_model=List[EmailLogResponse])
async def get_email_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    이메일 발송 로그 조회
    """
    logs = db.query(EmailLog).order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs


@app.get("/api/v1/email/logs/{log_id}", response_model=EmailLogResponse)
async def get_email_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    특정 이메일 발송 로그 상세 조회
    """
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="로그를 찾을 수 없습니다.")
    return log


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)

