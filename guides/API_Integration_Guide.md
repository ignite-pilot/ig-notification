# IG Notification – HTTP API 연동 가이드 (LLM용)

본 문서는 LLM이 IG Notification REST API를 호출할 때 필요한 최소 정보를 제공합니다.

## 개요
- Base URL:
  - 로컬 기본: `http://localhost:8101`
  - Alpha: `https://alpha.ig-notification.ig-pilot.com:8101` (배포 설정에 따름)
- 인증: `X-API-Key` 헤더 (환경에 따라 필수/옵션)
- Rate Limit: `/api/v1/email/send` 10회/분 (slowapi)
- 포트/호스트 설정: `backend/config/*.py` 및 `PHASE` 환경변수에 따름

## 엔드포인트

### 1) POST /api/v1/email/send
- 목적: 이메일 발송 및 로그 기록
- Content-Type: `multipart/form-data`
- 필드:
  - `recipient_emails` (string, 필수): JSON 문자열 배열, 예 `["a@ex.com","b@ex.com"]`
  - `sender_email` (string, 필수)
  - `smtp_host` (string, 필수)
  - `smtp_port` (int, 필수)
  - `smtp_username` (string, 선택) - **⚠️ 대부분의 SMTP 서버는 인증 필수**
  - `smtp_password` (string, 선택) - **⚠️ smtp_username과 함께 제공 필요**
  - `use_ssl` (bool, 기본 true)
  - `verify_ssl` (bool, 기본 true) – self-signed 허용 시 false
  - `cc_emails` (string, 선택): JSON 문자열 배열
  - `bcc_emails` (string, 선택): JSON 문자열 배열
  - `subject` (string, 필수)
  - `body` (string, 필수) – HTML 가능
  - `files` (file[], 선택): 최대 10개, 총 30MB
- 응답 200:
  - `{ log_id: UUID, status: "success"|"failed"|"pending", message: string, created_at: ISO8601 }`
- 주요 검증/제약:
  - 수신자 1~100개, 이메일 형식 검증
  - 첨부 개수 ≤10, 총 크기 ≤30MB
  - 허용 확장자: `.pdf .doc .docx .txt .jpg .jpeg .png .gif .xls .xlsx .csv`
  - 허용 MIME: `application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/plain, text/csv, image/jpeg, image/png, image/gif`

#### 예시 cURL
```bash
curl -X POST "http://localhost:8101/api/v1/email/send" \
  -H "X-API-Key: <API_KEY>" \
  -F 'recipient_emails=["user@example.com"]' \
  -F 'sender_email=noreply@example.com' \
  -F 'smtp_host=smtp.gmail.com' \
  -F 'smtp_port=465' \
  -F 'smtp_username=noreply@example.com' \
  -F 'smtp_password=app-password' \
  -F 'use_ssl=true' \
  -F 'verify_ssl=true' \
  -F 'subject=테스트 메일' \
  -F 'body=본문입니다' \
  -F "files=@/path/to/hello.txt"
```

### 2) GET /api/v1/email/logs
- 목적: 이메일 로그 목록 조회
- 쿼리: `skip` (기본 0), `limit` (기본 100)
- 응답 200: `EmailLog[]` (최신순)

### 3) GET /api/v1/email/logs/{log_id}
- 목적: 특정 이메일 로그 상세 조회
- 경로 파라미터: `log_id` (UUID)
- 응답 200: `EmailLog`
- 미존재 시 404

### 4) GET /health
- 목적: 서비스 상태 확인
- 응답 200: `{ "status": "ok" }`

## 오류 및 상태 코드
- 400: 검증 실패 (수신자 개수, 첨부 제한, 잘못된 JSON 등)
- 401: API Key 불일치/누락 (환경에서 API Key 사용 시)
- 404: 로그 미존재
- 422: 필수 폼 필드 누락/형식 오류
- 429: rate limit 초과 (slowapi)
- 500: 서버 오류 (상세 메시지 제한)

## LLM을 위한 체크리스트
- `recipient_emails`는 JSON 문자열 배열로 직렬화 후 전송
- **SMTP 인증**: 대부분의 SMTP 서버(Gmail, Outlook 등)는 `smtp_username`과 `smtp_password`가 필수입니다. 둘 중 하나라도 누락되면 발송 실패합니다.
- 첨부파일 크기/개수/확장자 사전 검증
- 반복 호출 시 중복 발송 주의 (idempotency 없음)
- Alpha 환경에서는 `X-API-Key` 포함 여부를 사전 확인
- Self-signed 서버 사용 시 `verify_ssl=false` 설정 가능


