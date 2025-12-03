from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import logging

from database import get_db, init_db, EmailLog
from models import EmailSendRequest, EmailSendResponse, EmailLogResponse
from email_service import EmailService
from config import settings

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="IG Notification API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed: {str(e)}. Server will continue without database.")


@app.post("/api/v1/email/send", response_model=EmailSendResponse)
async def send_email(
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
        
        # Process attachments
        attachments = []
        total_size = 0
        if files:
            if len(files) > 10:
                raise HTTPException(status_code=400, detail="첨부파일은 최대 10개까지 가능합니다.")
            
            for file in files:
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
    except Exception as e:
        logger.error(f"이메일 발송 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


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

