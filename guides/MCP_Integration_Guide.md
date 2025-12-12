# IG Notification – MCP 연동 가이드 (LLM용)

본 문서는 LLM 또는 MCP 클라이언트가 IG Notification 시스템과 통신하기 위한 최소 지침을 제공합니다.

## 개요
- 프로토콜: JSON-RPC over HTTP POST
- 기본 포트: `MCP_PORT` (기본 8102, `backend/config/local.py` 참조)
- 기본 호스트:
  - 로컬: `http://localhost`
  - Alpha: `https://alpha.ig-notification.ig-pilot.com`
- CORS: `config/cors_allowed_origins.json` 및 `config/*.py` 설정을 따름
- 인증: 기본적으로 없음. Alpha 환경에서 필요 시 API Key를 별도 협의 후 헤더로 전달 (`X-API-Key`).

## 엔드포인트
- Path: `/mcp`
- Method: `POST`
- Content-Type: `application/json`

## 지원 메서드

### 1) send_email
- 설명: 이메일 발송 및 로그 기록
- 파라미터 (`params`):
  - `recipient_emails`: string[] (필수, 1~100)
  - `sender_email`: string (필수)
  - `smtp_host`: string (필수)
  - `smtp_port`: number (필수)
  - `smtp_username`: string (선택)
  - `smtp_password`: string (선택)
  - `use_ssl`: boolean (기본 true)
  - `cc_emails`: string[] (선택)
  - `bcc_emails`: string[] (선택)
  - `subject`: string (필수)
  - `body`: string (필수, HTML 가능)
  - `attachments`: { filename: string, content_base64: string }[] (선택, 최대 10개, 총 30MB)
- 응답 (`result`):
  - `log_id`: string (UUID)
  - `status`: `"success" | "failed" | "pending"`
  - `message`: string
  - `created_at`: ISO8601 string
- 에러:
  - -32602: 잘못된 요청/검증 실패
  - -32603: 서버 내부 오류

#### 예시 요청
```json
{
  "method": "send_email",
  "params": {
    "recipient_emails": ["user@example.com"],
    "sender_email": "noreply@example.com",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 465,
    "smtp_username": "noreply@example.com",
    "smtp_password": "app-password",
    "use_ssl": true,
    "subject": "테스트 메일",
    "body": "본문입니다",
    "attachments": [
      {
        "filename": "hello.txt",
        "content_base64": "aGVsbG8gd29ybGQ="
      }
    ]
  }
}
```

### 2) get_email_log
- 설명: 특정 로그 상세 조회
- 파라미터:
  - `log_id`: string (UUID, 필수)
- 응답 (`result`): `EmailLog` 필드 전체 (id, sender_email, recipient_emails, cc/bcc, subject, body, smtp_host/port, use_ssl, status, error_message, attachment_count, total_attachment_size, created_at, sent_at)
- 에러:
  - -32602: 파라미터 없음 또는 로그 미존재
  - -32603: 서버 내부 오류

### 3) list_email_logs
- 설명: 로그 목록 조회
- 파라미터:
  - `skip`: number (기본 0)
  - `limit`: number (기본 100)
- 응답 (`result`):
  - `logs`: `EmailLog` 요약 배열
  - `total`: number
- 에러:
  - -32603: 서버 내부 오류

## 제한 사항 및 검증
- 수신자: 1~100개
- 첨부파일: 최대 10개, 총 30MB
- 허용 확장자: `.pdf, .doc, .docx, .txt, .jpg, .jpeg, .png, .gif, .xls, .xlsx, .csv`
- 허용 MIME: `application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/plain, text/csv, image/jpeg, image/png, image/gif`

## 상태 코드 매핑
- JSON-RPC 에러 코드 외, HTTP 상태:
  - 200: 성공(JSON-RPC result 포함)
  - 4xx/5xx: JSON-RPC error 오브젝트 포함

## 실행/접속 정보
- 로컬 개발 기본값:
  - MCP: `http://localhost:8102/mcp`
  - Health: FastAPI 서비스 `/health` (8101)로 별도 확인 가능
- Alpha 환경:
  - MCP: `https://alpha.ig-notification.ig-pilot.com:mcp_port/mcp` (실제 포트/도메인은 배포 설정에 따름)

## LLM을 위한 프롬프트 힌트
- 요청 전 유효성 검사: 수신자 수(1~100), 첨부 크기/개수, 허용 확장자 확인
- 인증 필요 시 `X-API-Key` 헤더를 추가
- 타임아웃/재시도 시 idempotency 고려: 동일 파라미터 재전송은 중복 메일을 유발할 수 있음


