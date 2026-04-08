from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class EmailSendRequest(BaseModel):
    recipient_emails: List[EmailStr]
    sender_email: EmailStr
    smtp_host: str
    smtp_port: int
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_ssl: bool = True
    cc_emails: Optional[List[EmailStr]] = None
    bcc_emails: Optional[List[EmailStr]] = None
    subject: str
    body: str
    attachments: Optional[List[str]] = None  # Base64 encoded files
    
    @field_validator('recipient_emails')
    @classmethod
    def validate_recipients(cls, v):
        if len(v) > 100:
            raise ValueError('최대 100명까지 발송 가능합니다.')
        if len(v) == 0:
            raise ValueError('받는 사람 이메일을 최소 1개 이상 입력해주세요.')
        return v


class EmailSendResponse(BaseModel):
    log_id: UUID
    status: str
    message: str
    created_at: datetime


class EmailLogResponse(BaseModel):
    id: UUID
    sender_email: str
    recipient_emails: List[str]
    cc_emails: Optional[List[str]]
    bcc_emails: Optional[List[str]]
    subject: str
    body: str
    smtp_host: str
    smtp_port: int
    use_ssl: str
    status: str
    error_message: Optional[str]
    attachment_count: int
    total_attachment_size: int
    created_at: datetime
    sent_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PushSendResponse(BaseModel):
    logId: UUID
    status: str
    message: str
    successCount: int
    failureCount: int
    createdAt: datetime


class PushLogResponse(BaseModel):
    id: UUID
    firebase_project_id: str
    title: str
    body: str
    data: Optional[Dict[str, Any]]
    device_tokens: List[str]
    success_count: int
    failure_count: int
    failed_tokens: Optional[List[str]]
    status: str
    error_message: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

