# IG Notification 보안 감사 보고서

## 🔴 심각한 보안 문제 (Critical)

### 1. 하드코딩된 민감 정보

**위치:**
- `backend/config.py` (라인 6): 데이터베이스 비밀번호 하드코딩
- `frontend/src/components/EmailForm.jsx` (라인 11): SMTP 비밀번호 하드코딩 (`bcasmtygslphzqnk`)
- `Requirement.md` (라인 40-48): GitHub 비밀번호, Personal Access Key, 데이터베이스 비밀번호 평문 노출

**위험도:** 🔴 Critical

**설명:**
- 데이터베이스 비밀번호, SMTP 비밀번호, GitHub Personal Access Key가 소스 코드에 평문으로 저장되어 있습니다.
- 이 정보들이 Git 저장소에 커밋되면 누구나 접근할 수 있습니다.

**권장 조치:**
1. 모든 민감 정보를 환경 변수로 이동
2. `.env` 파일을 `.gitignore`에 추가
3. `Requirement.md`에서 민감 정보 제거
4. 이미 노출된 비밀번호/키는 즉시 변경
5. Git 히스토리에서 민감 정보 제거 (git filter-branch 또는 BFG Repo-Cleaner 사용)

**수정 예시:**
```python
# backend/config.py
class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")  # 환경 변수에서 읽기
    api_port: int = int(os.getenv("API_PORT", "8101"))
    mcp_port: int = int(os.getenv("MCP_PORT", "8102"))
```

### 2. CORS 설정이 모든 Origin 허용

**위치:**
- `backend/main.py` (라인 23): `allow_origins=["*"]`
- `backend/mcp_server.py` (라인 271): CORS가 모든 origin 허용

**위험도:** 🔴 Critical

**설명:**
- 모든 도메인에서 API를 호출할 수 있어 CSRF 공격에 취약합니다.
- 악의적인 웹사이트가 사용자의 브라우저를 통해 API를 호출할 수 있습니다.

**권장 조치:**
```python
# 프로덕션 환경에서는 특정 도메인만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",  # 개발 환경
        "https://yourdomain.com",  # 프로덕션 도메인
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. 인증/인가 부재

**위험도:** 🔴 Critical

**설명:**
- API 엔드포인트에 인증이 없어 누구나 이메일을 발송할 수 있습니다.
- 악의적인 사용자가 대량의 이메일을 발송하여 스팸 발송 도구로 악용될 수 있습니다.

**권장 조치:**
1. API 키 기반 인증 구현
2. Rate limiting 적용
3. IP 화이트리스트 (선택사항)

**수정 예시:**
```python
from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("API_KEY")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/api/v1/email/send", dependencies=[Depends(verify_api_key)])
async def send_email(...):
    ...
```

## 🟡 중간 수준 보안 문제 (High)

### 4. 파일 업로드 보안 검증 부족

**위치:**
- `backend/main.py` (라인 80-90): 파일 타입 검증 없음

**위험도:** 🟡 High

**설명:**
- 업로드된 파일의 MIME 타입이나 확장자를 검증하지 않습니다.
- 악성 파일 업로드 가능성이 있습니다.

**권장 조치:**
```python
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.png'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'image/jpeg',
    'image/png'
}

for file in files:
    # 확장자 검증
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="허용되지 않은 파일 형식입니다.")
    
    # MIME 타입 검증
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="허용되지 않은 파일 형식입니다.")
```

### 5. 입력 검증 부족

**위험도:** 🟡 High

**설명:**
- 이메일 주소 형식 검증이 없습니다.
- SQL Injection은 SQLAlchemy ORM 사용으로 방지되지만, 추가 검증이 필요합니다.

**권장 조치:**
```python
from email_validator import validate_email, EmailNotValidError

def validate_email_list(emails: List[str]) -> bool:
    for email in emails:
        try:
            validate_email(email)
        except EmailNotValidError:
            return False
    return True
```

### 6. Rate Limiting 부재

**위험도:** 🟡 High

**설명:**
- API 호출 횟수 제한이 없어 DoS 공격이나 스팸 발송에 취약합니다.

**권장 조치:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/email/send")
@limiter.limit("10/minute")  # 분당 10회 제한
async def send_email(...):
    ...
```

### 7. 로깅에 민감 정보 노출 가능성

**위치:**
- `backend/main.py`: 로깅 레벨이 DEBUG로 설정됨

**위험도:** 🟡 High

**설명:**
- DEBUG 레벨 로깅은 프로덕션에서 민감 정보를 노출할 수 있습니다.

**권장 조치:**
```python
import os

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
```

## 🟢 낮은 수준 보안 문제 (Medium)

### 8. HTTPS 강제 없음

**위험도:** 🟢 Medium

**설명:**
- HTTP로 통신하면 데이터가 평문으로 전송됩니다.

**권장 조치:**
- 프로덕션 환경에서는 HTTPS를 사용하고 HTTP를 HTTPS로 리다이렉트

### 9. 의존성 취약점 확인 필요

**위험도:** 🟢 Medium

**권장 조치:**
```bash
# Python 의존성 취약점 스캔
pip install safety
safety check

# npm 의존성 취약점 스캔
npm audit
```

### 10. 에러 메시지에 과도한 정보 노출

**위치:**
- `backend/main.py` (라인 152): 전체 에러 메시지 반환

**위험도:** 🟢 Medium

**권장 조치:**
```python
except Exception as e:
    logger.error(f"이메일 발송 중 오류: {str(e)}")
    # 프로덕션에서는 상세 에러를 숨김
    raise HTTPException(
        status_code=500, 
        detail="서버 오류가 발생했습니다. 관리자에게 문의하세요."
    )
```

## 보안 체크리스트

### 즉시 조치 필요 (Critical)
- [ ] 모든 하드코딩된 비밀번호/키 제거
- [ ] 환경 변수로 민감 정보 이동
- [ ] `.env` 파일 `.gitignore`에 추가
- [ ] 노출된 비밀번호/키 즉시 변경
- [ ] CORS 설정 제한
- [ ] API 인증 구현

### 단기 조치 필요 (High)
- [ ] 파일 업로드 검증 추가
- [ ] 입력 검증 강화
- [ ] Rate limiting 구현
- [ ] 로깅 레벨 조정

### 중기 조치 필요 (Medium)
- [ ] HTTPS 강제
- [ ] 의존성 취약점 스캔 및 업데이트
- [ ] 에러 메시지 개선

## 보안 모범 사례

1. **민감 정보 관리**
   - 모든 비밀번호, 키, 토큰은 환경 변수로 관리
   - `.env` 파일은 절대 Git에 커밋하지 않음
   - 비밀번호는 강력한 해시 알고리즘으로 저장 (bcrypt, argon2 등)

2. **인증 및 인가**
   - 모든 API 엔드포인트에 인증 적용
   - JWT 또는 API 키 기반 인증 사용
   - 역할 기반 접근 제어 (RBAC) 구현

3. **입력 검증**
   - 모든 사용자 입력 검증
   - 화이트리스트 방식 사용
   - SQL Injection, XSS 방지

4. **보안 헤더**
   - Security headers 추가 (CSP, X-Frame-Options 등)
   - HTTPS 강제

5. **모니터링 및 로깅**
   - 보안 이벤트 로깅
   - 이상 행위 감지
   - 정기적인 보안 감사

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security.html)

