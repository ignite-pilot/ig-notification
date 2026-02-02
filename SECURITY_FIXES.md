# 보안 수정 사항

## 적용된 보안 수정 사항

### ✅ 1. 하드코딩된 비밀번호 제거
- `backend/config.py`: 데이터베이스 URL을 환경 변수에서 읽도록 수정
- `frontend/src/components/EmailForm.jsx`: 하드코딩된 SMTP 비밀번호 제거
- `.env.example` 파일 생성 (환경 변수 템플릿)

### ✅ 2. CORS 설정 제한
- `backend/main.py`: `allow_origins=["*"]` → 환경 변수에서 허용 도메인 읽기
- `backend/mcp_server.py`: MCP 서버에도 동일한 CORS 제한 적용
- 기본값: `http://localhost:8100` (개발 환경)

### ✅ 3. API 인증 추가
- API 키 기반 인증 구현 (선택적)
- `X-API-Key` 헤더로 인증
- `API_KEY` 환경 변수가 설정된 경우에만 활성화

### ✅ 4. 파일 업로드 검증 강화
- 허용된 파일 확장자 검증 (`.pdf`, `.doc`, `.docx`, `.txt`, `.jpg`, `.png` 등)
- MIME 타입 검증
- 파일명 검증

### ✅ 5. 입력 검증 강화
- 이메일 주소 형식 검증 (`email-validator` 사용)
- 받는 사람, 보내는 사람, 참조, 숨은 참조 모두 검증

### ✅ 6. Rate Limiting 추가
- `slowapi` 라이브러리 사용
- 이메일 발송 API: 분당 10회 제한
- IP 기반 제한

### ✅ 7. 로깅 레벨 조정
- 환경 변수 `LOG_LEVEL`로 제어
- 기본값: `INFO` (프로덕션 적합)
- DEBUG 레벨은 개발 환경에서만 사용

### ✅ 8. 에러 메시지 개선
- 프로덕션에서 상세 에러 메시지 숨김
- 보안 정보 노출 방지

## 환경 변수 설정

`.env` 파일에 다음 변수를 설정하세요:

```bash
# 필수
DATABASE_URL=mysql+pymysql://user:password@host:port/database_name?charset=utf8mb4
API_PORT=8101
MCP_PORT=8102

# 선택사항 (보안 강화)
API_KEY=your-secret-api-key-here  # API 키 인증 활성화
ALLOWED_ORIGINS=http://localhost:8100,https://yourdomain.com  # CORS 허용 도메인
LOG_LEVEL=INFO  # 로깅 레벨
```

## 사용 방법

### API 키 인증 사용 (선택사항)

1. `.env` 파일에 `API_KEY` 설정:
```bash
API_KEY=your-secret-api-key-here
```

2. API 요청 시 헤더에 추가:
```bash
curl -X POST http://localhost:8101/api/v1/email/send \
  -H "X-API-Key: your-secret-api-key-here" \
  -F "recipient_emails=[\"test@example.com\"]" \
  ...
```

### CORS 설정

`.env` 파일에서 허용할 도메인을 설정:
```bash
ALLOWED_ORIGINS=http://localhost:8100,https://yourdomain.com
```

### 로깅 레벨 조정

```bash
LOG_LEVEL=DEBUG  # 개발 환경
LOG_LEVEL=INFO   # 프로덕션 (기본값)
```

## 주의사항

1. **`.env` 파일은 절대 Git에 커밋하지 마세요**
   - `.gitignore`에 이미 포함되어 있습니다
   - `.env.example` 파일만 커밋하세요

2. **프로덕션 환경에서는 반드시:**
   - `API_KEY` 설정
   - `ALLOWED_ORIGINS`에 실제 도메인만 추가
   - `LOG_LEVEL=INFO` 또는 `WARNING` 사용
   - HTTPS 사용

3. **노출된 비밀번호/키는 즉시 변경하세요:**
   - GitHub Personal Access Key
   - 데이터베이스 비밀번호
   - SMTP 비밀번호

## 다음 단계

추가로 권장되는 보안 조치:

1. **의존성 취약점 스캔**
   ```bash
   pip install safety
   safety check
   npm audit
   ```

2. **HTTPS 강제**
   - 프로덕션 환경에서 HTTPS 사용
   - HTTP를 HTTPS로 리다이렉트

3. **보안 헤더 추가**
   - Content-Security-Policy
   - X-Frame-Options
   - X-Content-Type-Options

4. **정기적인 보안 감사**
   - 정기적으로 `SECURITY_AUDIT.md` 확인
   - 의존성 업데이트

