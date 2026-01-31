from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
import hmac
from pathlib import Path

from database import get_db, init_db, EmailLog, engine
from models import EmailSendResponse, EmailLogResponse
from email_service import EmailService
from settings import settings

# 로깅 레벨을 환경 변수에서 읽기
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_db()
        logger.info(f"Database initialized. Connection URL: {settings.database_url[:50]}...")
        # 테이블 존재 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Database tables: {tables}")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}. Server will continue without database.")
        logger.exception(e)
    yield
    # Shutdown (필요한 경우 정리 작업)

app = FastAPI(
    title="IG Notification API", 
    version="1.0.0", 
    lifespan=lifespan,
    # 보안 헤더 설정
    docs_url="/api/docs" if settings.env_name == "local" else None,  # 프로덕션에서는 docs 비활성화
    redoc_url="/api/redoc" if settings.env_name == "local" else None,  # 프로덕션에서는 redoc 비활성화
    openapi_url="/api/openapi.json" if settings.env_name == "local" else None,  # 프로덕션에서는 openapi 비활성화
)

# Validation error 핸들러 추가
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422 Validation Error를 상세하게 로깅"""
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    
    # body는 로깅만 하고 응답에는 포함하지 않음 (UploadFile 직렬화 문제 방지)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Rate Limiting 설정
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정 - 보안을 위해 제한적으로 설정
# 통합 서버이므로 같은 origin에서 서빙되지만, 외부 API 호출을 위한 CORS 설정
cors_origins = settings.allowed_origins_list if settings.allowed_origins_list else []
# Local 환경에서는 localhost 허용
if settings.env_name == "local":
    if "http://localhost:8101" not in cors_origins:
        cors_origins.append("http://localhost:8101")
    if "http://127.0.0.1:8101" not in cors_origins:
        cors_origins.append("http://127.0.0.1:8101")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # 명시적으로 허용된 origin만
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],  # 필요한 헤더만 명시
    expose_headers=["Content-Type", "Content-Length"],
    max_age=3600,  # Preflight 요청 캐시 시간
)

# Frontend 정적 파일 서빙 설정
# 프로젝트 루트 기준으로 frontend/dist 폴더를 찾음
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

# 정적 파일이 존재하는 경우에만 마운트
# 주의: 이 핸들러는 API 라우트 이후에 등록되어야 함 (라우트 우선순위)
if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
    # 정적 파일 (JS, CSS 등) 서빙
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")

# API 키 인증 (선택적 - API_KEY가 설정된 경우에만 활성화)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    API 키 검증 (API_KEY가 설정된 경우에만 활성화)
    보안: Constant-time 비교를 사용하여 timing attack 방지
    """
    if settings.api_key:
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="API key is required. Please provide a valid X-API-Key header."
            )
        # Constant-time 비교를 위한 구현 (timing attack 방지)
        # hmac.compare_digest는 constant-time 비교를 보장
        try:
            if not hmac.compare_digest(x_api_key.encode('utf-8'), settings.api_key.encode('utf-8')):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key. Please provide a valid X-API-Key header."
                )
        except (UnicodeEncodeError, AttributeError):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key format."
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
    use_ssl: str = Form("true"),  # Form 데이터는 문자열로 받아서 변환
    verify_ssl: str = Form("true"),  # SSL 인증서 검증 여부
    cc_emails: Optional[str] = Form(None),  # JSON string
    bcc_emails: Optional[str] = Form(None),  # JSON string
    subject: str = Form(...),
    body: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    """
    이메일 발송 API
    files 파라미터는 multipart/form-data에서 여러 파일을 받을 수 있습니다.
    """
    import json
    from email_validator import validate_email, EmailNotValidError
    
    try:
        # files가 리스트가 아닌 경우 리스트로 정규화
        if not isinstance(files, list):
            files = [files] if files else []
        
        # Convert string boolean to actual boolean
        use_ssl_bool = use_ssl.lower() in ("true", "1", "yes") if isinstance(use_ssl, str) else bool(use_ssl)
        verify_ssl_bool = verify_ssl.lower() in ("true", "1", "yes") if isinstance(verify_ssl, str) else bool(verify_ssl)
        
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
                except EmailNotValidError:
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
        
        if files and len(files) > 0:
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
                        detail="허용되지 않은 파일 타입입니다."
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
        try:
            email_log = EmailLog(
                sender_email=sender_email,
                recipient_emails=recipient_list,
                cc_emails=cc_list,
                bcc_emails=bcc_list,
                subject=subject,
                body=body,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                use_ssl="true" if use_ssl_bool else "false",
                status="pending",
                attachment_count=len(attachments),
                total_attachment_size=total_size
            )
            db.add(email_log)
            db.commit()
            db.refresh(email_log)
            logger.info(f"Email log created with ID: {email_log.id}")
        except Exception as e:
            logger.error(f"Failed to create email log: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"로그 저장 실패: {str(e)}"
            )
        
        # Send email
        success, error_message = await EmailService.send_email(
            recipient_emails=recipient_list,
            sender_email=sender_email,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            use_ssl=use_ssl_bool,
            subject=subject,
            body=body,
            cc_emails=cc_list,
            bcc_emails=bcc_list,
            attachments=attachments if attachments else None,
            verify_ssl=verify_ssl_bool
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
    try:
        logs = db.query(EmailLog).order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(logs)} email logs from database")
        return logs
    except Exception as e:
        logger.error(f"Error retrieving email logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="로그 조회 중 오류가 발생했습니다."
        )


@app.get("/api/v1/email/logs/{log_id}", response_model=EmailLogResponse)
async def get_email_log(
    log_id: str,  # MySQL에서는 UUID를 문자열로 저장하므로 str로 변경
    db: Session = Depends(get_db)
):
    """
    특정 이메일 발송 로그 상세 조회
    """
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="로그를 찾을 수 없습니다.")
    return log


@app.get("/api/health")
async def health_check():
    """Health Check API - CommonWebDevGuide.md에 따라 /api/health 경로 사용"""
    return {"status": "ok", "service": "ig-notification"}


# Frontend가 없을 때 루트 경로에 대한 기본 응답
@app.get("/")
async def root():
    """루트 경로 - Frontend가 있으면 SPA로 리다이렉트, 없으면 API 정보 표시"""
    if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
        index_file = FRONTEND_DIST_DIR / "index.html"
        return FileResponse(
            str(index_file),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    else:
        # Frontend가 없을 때 API 정보 표시
        from fastapi.responses import HTMLResponse
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IG Notification API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { color: #007bff; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>IG Notification API</h1>
            <p>서버가 정상적으로 실행 중입니다.</p>
            <h2>사용 가능한 API 엔드포인트:</h2>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/api/health">/api/health</a> - Health Check
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/v1/email/send - 이메일 발송
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/api/v1/email/logs">/api/v1/email/logs</a> - 이메일 로그 조회
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/v1/email/logs/{log_id} - 로그 상세 조회
            </div>
            <p style="margin-top: 30px;">
                <a href="/api/docs">API 문서 보기</a> (로컬 환경)
            </p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


# Frontend SPA 라우팅을 위한 fallback 핸들러
# 모든 API 라우트 이후에 등록되어야 함 (라우트 우선순위)
if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        """
        Frontend SPA 라우팅을 위한 fallback 핸들러
        API 경로가 아닌 모든 요청을 index.html로 리다이렉트
        """
        # API 경로는 제외 (이미 위에서 처리됨)
        if full_path.startswith("api/") or full_path.startswith("mcp") or full_path.startswith("assets"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # 정적 파일 요청 처리 (favicon, robots.txt 등)
        static_file = FRONTEND_DIST_DIR / full_path
        # 보안: 경로 traversal 공격 방지 (상위 디렉토리 접근 차단)
        try:
            static_file.resolve().relative_to(FRONTEND_DIST_DIR.resolve())
        except ValueError:
            # 경로가 FRONTEND_DIST_DIR 밖에 있으면 차단
            raise HTTPException(status_code=403, detail="Forbidden")
        
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # 그 외 모든 요청은 index.html로 (SPA 라우팅)
        index_file = FRONTEND_DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(
                str(index_file),
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    # 컨테이너에서는 항상 0.0.0.0 사용 (도메인은 ALB에서 처리)
    host = "0.0.0.0"
    uvicorn.run(app, host=host, port=settings.api_port)

