# IG Notification API 문서

## 서버 정보

- **REST API 서버**: `http://localhost:8101`
- **MCP 서버**: `http://localhost:8102`
- **Swagger UI**: `http://localhost:8101/docs`
- **ReDoc**: `http://localhost:8101/redoc`

## REST API 엔드포인트

### 1. 이메일 발송

**엔드포인트**: `POST /api/v1/email/send`

**요청 형식**: `multipart/form-data`

**Content-Type**: `multipart/form-data`

**필수 파라미터**:
- `recipient_emails` (string, JSON 형식): 받는 사람 이메일 배열 (JSON string)
  - 예: `["email1@example.com", "email2@example.com"]`
  - 최대 100명
- `sender_email` (string): 보내는 사람 이메일
- `smtp_host` (string): SMTP 서버 주소
- `smtp_port` (integer): SMTP 포트 번호
- `subject` (string): 이메일 제목
- `body` (string): 이메일 본문

**선택 파라미터**:
- `smtp_username` (string, optional): SMTP 사용자명
- `smtp_password` (string, optional): SMTP 비밀번호
- `use_ssl` (boolean, default: true): SSL 사용 여부
- `verify_ssl` (boolean, default: true): SSL 인증서 검증 여부
- `cc_emails` (string, JSON 형식, optional): 참조 이메일 배열 (JSON string)
- `bcc_emails` (string, JSON 형식, optional): 숨은 참조 이메일 배열 (JSON string)
- `files` (file[], optional): 첨부파일 (최대 10개, 총 30MB)

**요청 예시 (cURL)**:
```bash
curl -X POST http://localhost:8101/api/v1/email/send \
  -F "recipient_emails=[\"test@example.com\"]" \
  -F "sender_email=sender@example.com" \
  -F "smtp_host=smtp.gmail.com" \
  -F "smtp_port=587" \
  -F "smtp_username=your-email@gmail.com" \
  -F "smtp_password=your-app-password" \
  -F "use_ssl=true" \
  -F "verify_ssl=true" \
  -F "subject=Test Email" \
  -F "body=This is a test email" \
  -F "files=@/path/to/file.pdf"
```

**요청 예시 (Python requests)**:
```python
import requests
import json

url = "http://localhost:8101/api/v1/email/send"

data = {
    "recipient_emails": json.dumps(["test@example.com"]),
    "sender_email": "sender@example.com",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "use_ssl": True,
    "verify_ssl": True,
    "subject": "Test Email",
    "body": "This is a test email"
}

files = {
    "files": ("document.pdf", open("/path/to/file.pdf", "rb"), "application/pdf")
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

**요청 예시 (JavaScript/Node.js)**:
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('recipient_emails', JSON.stringify(['test@example.com']));
form.append('sender_email', 'sender@example.com');
form.append('smtp_host', 'smtp.gmail.com');
form.append('smtp_port', '587');
form.append('smtp_username', 'your-email@gmail.com');
form.append('smtp_password', 'your-app-password');
form.append('use_ssl', 'true');
form.append('verify_ssl', 'true');
form.append('subject', 'Test Email');
form.append('body', 'This is a test email');
form.append('files', fs.createReadStream('/path/to/file.pdf'));

axios.post('http://localhost:8101/api/v1/email/send', form, {
  headers: form.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

**성공 응답 (200 OK)**:
```json
{
  "log_id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
  "status": "success",
  "message": "이메일이 성공적으로 발송되었습니다.",
  "created_at": "2025-12-04T13:00:00.000000"
}
```

**에러 응답 (400 Bad Request)**:
```json
{
  "detail": "최대 100명까지 발송 가능합니다."
}
```

**에러 응답 (422 Unprocessable Entity)**:
```json
{
  "detail": [
    {
      "loc": ["body", "recipient_emails"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 2. 이메일 로그 목록 조회

**엔드포인트**: `GET /api/v1/email/logs`

**요청 형식**: Query Parameters

**파라미터**:
- `skip` (integer, optional, default: 0): 건너뛸 레코드 수
- `limit` (integer, optional, default: 100): 조회할 레코드 수

**요청 예시**:
```bash
curl http://localhost:8101/api/v1/email/logs?skip=0&limit=10
```

**응답 예시**:
```json
[
  {
    "id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
    "sender_email": "sender@example.com",
    "recipient_emails": ["test@example.com"],
    "cc_emails": null,
    "bcc_emails": null,
    "subject": "Test Email",
    "body": "This is a test email",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "use_ssl": "true",
    "status": "success",
    "error_message": null,
    "attachment_count": 0,
    "total_attachment_size": 0,
    "created_at": "2025-12-04T13:00:00.000000",
    "sent_at": "2025-12-04T13:00:05.000000"
  }
]
```

### 3. 이메일 로그 상세 조회

**엔드포인트**: `GET /api/v1/email/logs/{log_id}`

**경로 파라미터**:
- `log_id` (UUID): 로그 ID

**요청 예시**:
```bash
curl http://localhost:8101/api/v1/email/logs/027fc027-2da1-44d6-ac75-b5e496eafe47
```

**응답 예시**:
```json
{
  "id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
  "sender_email": "sender@example.com",
  "recipient_emails": ["test@example.com"],
  "cc_emails": null,
  "bcc_emails": null,
  "subject": "Test Email",
  "body": "This is a test email",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "use_ssl": "true",
  "status": "success",
  "error_message": null,
  "attachment_count": 0,
  "total_attachment_size": 0,
  "created_at": "2025-12-04T13:00:00.000000",
  "sent_at": "2025-12-04T13:00:05.000000"
}
```

**에러 응답 (404 Not Found)**:
```json
{
  "detail": "로그를 찾을 수 없습니다."
}
```

### 4. 헬스 체크

**엔드포인트**: `GET /health`

**요청 예시**:
```bash
curl http://localhost:8101/health
```

**응답 예시**:
```json
{
  "status": "ok"
}
```

## MCP 서버 엔드포인트

### MCP 프로토콜 요청

**엔드포인트**: `POST /mcp`

**서버 URL**: `http://localhost:8102/mcp`

**요청 형식**: `application/json`

**Content-Type**: `application/json`

**요청 형식 (JSON-RPC 스타일)**:
```json
{
  "method": "send_email",
  "params": {
    "recipient_emails": ["test@example.com"],
    "sender_email": "sender@example.com",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "use_ssl": true,
    "subject": "Test Email",
    "body": "This is a test email"
  }
}
```

자세한 내용은 `MCP_CLIENT_GUIDE.md`를 참고하세요.

## 제한사항

- **받는 사람**: 최대 100명
- **첨부파일**: 최대 10개
- **첨부파일 총 크기**: 최대 30MB

## 에러 코드

### REST API 에러

- `400 Bad Request`: 잘못된 요청 (예: 받는 사람 수 초과, 첨부파일 크기 초과)
- `404 Not Found`: 리소스를 찾을 수 없음
- `422 Unprocessable Entity`: 필수 파라미터 누락 또는 형식 오류
- `500 Internal Server Error`: 서버 내부 오류

### MCP 에러

- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32700`: Parse error

## OpenAPI/Swagger 문서

FastAPI는 자동으로 OpenAPI 문서를 생성합니다. 다음 URL에서 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8101/docs
- **ReDoc**: http://localhost:8101/redoc
- **OpenAPI JSON**: http://localhost:8101/openapi.json

## 참고사항

1. **포트 변경**: 서버 포트가 변경된 경우 모든 URL의 포트 번호를 업데이트하세요.
2. **CORS**: 현재 모든 origin에서 접근 가능합니다. 프로덕션에서는 특정 도메인만 허용하도록 변경하세요.
3. **인증**: 현재 인증이 없습니다. 프로덕션에서는 인증을 추가하는 것을 권장합니다.

