# IG Notification System

공통 알림 발송 모듈로, 이메일 발송 기능을 제공하는 REST API 서비스입니다.

## 🌐 서비스 URL

**프로덕션 환경**: https://ig-notification.ig-pilot.com/

## 📋 주요 기능

- **이메일 발송**: SMTP 서버를 통한 이메일 발송
  - 최대 100명까지 일괄 발송 가능
  - 첨부파일 지원 (최대 10개, 총 30MB)
  - CC/BCC 지원
  - SSL/TLS 지원
- **발송 로그 관리**: 모든 발송 이력 데이터베이스 저장 및 조회
- **웹 UI**: 이메일 발송을 위한 사용자 친화적인 웹 인터페이스

## 🚀 빠른 시작

### API 호출 예시

#### 이메일 발송

```bash
curl -X POST "https://ig-notification.ig-pilot.com/api/v1/email/send" \
  -H "Content-Type: multipart/form-data" \
  -F 'recipient_emails=["recipient@example.com"]' \
  -F 'sender_email=sender@example.com' \
  -F 'smtp_host=smtp.gmail.com' \
  -F 'smtp_port=587' \
  -F 'smtp_username=your-email@gmail.com' \
  -F 'smtp_password=your-app-password' \
  -F 'use_ssl=true' \
  -F 'verify_ssl=true' \
  -F 'subject=테스트 이메일' \
  -F 'body=이메일 본문 내용'
```

#### 발송 로그 조회

```bash
# 전체 로그 조회
curl "https://ig-notification.ig-pilot.com/api/v1/email/logs"

# 특정 로그 상세 조회
curl "https://ig-notification.ig-pilot.com/api/v1/email/logs/{log_id}"
```

#### 헬스 체크

```bash
curl "https://ig-notification.ig-pilot.com/api/health"
```

## 📚 API 문서

### 엔드포인트

#### 1. 이메일 발송
- **POST** `/api/v1/email/send`
- **Content-Type**: `multipart/form-data`

**필수 파라미터**:
- `recipient_emails` (string, JSON 형식): 받는 사람 이메일 배열
  - 예: `["email1@example.com", "email2@example.com"]`
  - 최대 100명
- `sender_email` (string): 보내는 사람 이메일
- `smtp_host` (string): SMTP 서버 주소
- `smtp_port` (integer): SMTP 포트 번호
- `subject` (string): 이메일 제목
- `body` (string): 이메일 본문 (HTML 지원)

**선택 파라미터**:
- `smtp_username` (string): SMTP 사용자명
  - **⚠️ 중요**: 대부분의 SMTP 서버(Gmail, Outlook 등)는 인증이 필수입니다.
  - 인증이 필요한 경우 `smtp_username`과 `smtp_password`를 모두 제공해야 합니다.
- `smtp_password` (string): SMTP 비밀번호
  - Gmail의 경우 일반 비밀번호가 아닌 **앱 비밀번호(App Password)**를 사용해야 합니다.
- `use_ssl` (boolean, default: true): SSL 사용 여부
- `verify_ssl` (boolean, default: true): SSL 인증서 검증 여부
- `cc_emails` (string, JSON 형식): 참조 이메일 배열
- `bcc_emails` (string, JSON 형식): 숨은 참조 이메일 배열
- `files` (file[]): 첨부파일 (최대 10개, 총 30MB)

**응답 예시**:
```json
{
  "log_id": "uuid-string",
  "status": "success",
  "message": "이메일이 성공적으로 발송되었습니다.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 2. 발송 로그 조회
- **GET** `/api/v1/email/logs`
- **쿼리 파라미터**:
  - `skip` (integer, default: 0): 건너뛸 레코드 수
  - `limit` (integer, default: 100): 반환할 레코드 수

#### 3. 특정 로그 상세 조회
- **GET** `/api/v1/email/logs/{log_id}`
- **경로 파라미터**: `log_id` (UUID)

#### 4. 헬스 체크
- **GET** `/api/health`
- **응답**: `{"status": "ok", "service": "ig-notification"}`

## 🔒 보안

- **Rate Limiting**: `/api/v1/email/send` 엔드포인트는 분당 10회로 제한됩니다.
- **파일 검증**: 첨부파일은 허용된 확장자와 MIME 타입만 허용됩니다.
- **이메일 검증**: 모든 이메일 주소는 형식 검증을 거칩니다.

### 허용된 파일 형식

**확장자**: `.pdf`, `.doc`, `.docx`, `.txt`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.xls`, `.xlsx`, `.csv`

**MIME 타입**: `application/pdf`, `application/msword`, `text/plain`, `image/jpeg`, `image/png`, `image/gif` 등

## 🛠️ 개발 환경 설정

### 사전 요구사항

- Python 3.12+
- Node.js 20+
- PostgreSQL

### 로컬 개발 환경 실행

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export PHASE=local
python main.py
```

Backend는 `http://localhost:8101`에서 실행됩니다.

#### Frontend

```bash
cd frontend
npm install
export PHASE=local
npm run dev
```

Frontend는 `http://localhost:8100`에서 실행됩니다.

## 📦 배포

이 서비스는 AWS ECS (Elastic Container Service)를 통해 배포됩니다.

- **배포 URL**: https://ig-notification.ig-pilot.com/
- **포트**: 8101
- **환경**: Production (Alpha)

## 📖 상세 문서

- [API 문서](./API_DOCUMENTATION.md): 상세한 API 문서
- [배포 가이드](./DEPLOYMENT.md): 배포 및 환경 설정 가이드
- [API 연동 가이드](./guides/API_Integration_Guide.md): 외부 서비스 연동 가이드
- [MCP 연동 가이드](./guides/MCP_Integration_Guide.md): MCP 서버 연동 가이드

## 🐛 문제 해결

### 일반적인 오류

- **400 Bad Request**: 요청 파라미터 검증 실패
- **401 Unauthorized**: API Key 불일치 또는 누락
- **422 Unprocessable Entity**: 필수 필드 누락 또는 형식 오류
- **429 Too Many Requests**: Rate limit 초과
- **500 Internal Server Error**: 서버 오류

## 📝 라이선스

이 프로젝트는 private 프로젝트입니다.

## 👥 연락처

프로젝트 관련 문의사항이 있으시면 개발팀에 연락해주세요.

---

**서비스 상태**: 🟢 운영 중  
**최종 업데이트**: 2026-01-28
