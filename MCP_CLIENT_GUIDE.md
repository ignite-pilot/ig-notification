# IG Notification MCP 클라이언트 사용 가이드

외부 서비스에서 IG Notification MCP 서버를 사용하는 방법을 안내합니다.

## 중요: API 엔드포인트 정보

IG Notification 시스템은 두 가지 방식으로 제공됩니다:

### 1. REST API (포트 8101)
- **이메일 발송**: `POST http://localhost:8101/api/v1/email/send`
- **요청 형식**: `multipart/form-data`
- **로그 조회**: `GET http://localhost:8101/api/v1/email/logs`
- **상세 문서**: `API_DOCUMENTATION.md` 참고

### 2. MCP 서버 (포트 8102)
- **URL**: `http://localhost:8102/mcp`
- **프로토콜**: HTTP POST
- **Content-Type**: `application/json`
- **JSON-RPC 스타일 요청**

## MCP 서버 정보

## 사용 가능한 메서드

### 1. send_email - 이메일 발송

이메일을 발송합니다.

**요청 예시:**
```json
{
  "method": "send_email",
  "params": {
    "recipient_emails": ["recipient1@example.com", "recipient2@example.com"],
    "sender_email": "sender@example.com",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "use_ssl": true,
    "cc_emails": ["cc@example.com"],
    "bcc_emails": ["bcc@example.com"],
    "subject": "이메일 제목",
    "body": "이메일 본문",
    "attachments": [
      {
        "filename": "document.pdf",
        "content_base64": "base64-encoded-content"
      }
    ]
  }
}
```

**응답 예시:**
```json
{
  "result": {
    "log_id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
    "status": "success",
    "message": "이메일이 성공적으로 발송되었습니다.",
    "created_at": "2025-12-04T13:00:00.000000"
  }
}
```

**제한사항:**
- 받는 사람: 최대 100명
- 첨부파일: 최대 10개
- 첨부파일 총 크기: 최대 30MB

### 2. get_email_log - 로그 조회

특정 이메일 발송 로그를 조회합니다.

**요청 예시:**
```json
{
  "method": "get_email_log",
  "params": {
    "log_id": "027fc027-2da1-44d6-ac75-b5e496eafe47"
  }
}
```

**응답 예시:**
```json
{
  "result": {
    "id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
    "sender_email": "sender@example.com",
    "recipient_emails": ["recipient@example.com"],
    "cc_emails": ["cc@example.com"],
    "bcc_emails": null,
    "subject": "이메일 제목",
    "body": "이메일 본문",
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
}
```

### 3. list_email_logs - 로그 목록 조회

이메일 발송 로그 목록을 조회합니다.

**요청 예시:**
```json
{
  "method": "list_email_logs",
  "params": {
    "skip": 0,
    "limit": 10
  }
}
```

**응답 예시:**
```json
{
  "result": {
    "logs": [
      {
        "id": "027fc027-2da1-44d6-ac75-b5e496eafe47",
        "sender_email": "sender@example.com",
        "recipient_emails": ["recipient@example.com"],
        "subject": "이메일 제목",
        "status": "success",
        "created_at": "2025-12-04T13:00:00.000000",
        "sent_at": "2025-12-04T13:00:05.000000"
      }
    ],
    "total": 1
  }
}
```

## 클라이언트 구현 예제

### Python 예제

```python
import requests
import json
import base64

MCP_SERVER_URL = "http://localhost:8102/mcp"

def send_email_via_mcp(recipient_emails, sender_email, smtp_host, smtp_port, 
                       smtp_username, smtp_password, subject, body, 
                       attachments=None, cc_emails=None, bcc_emails=None):
    """
    MCP를 통해 이메일 발송
    """
    request_data = {
        "method": "send_email",
        "params": {
            "recipient_emails": recipient_emails,
            "sender_email": sender_email,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_username": smtp_username,
            "smtp_password": smtp_password,
            "use_ssl": True,
            "subject": subject,
            "body": body
        }
    }
    
    if cc_emails:
        request_data["params"]["cc_emails"] = cc_emails
    if bcc_emails:
        request_data["params"]["bcc_emails"] = bcc_emails
    if attachments:
        # 파일을 base64로 인코딩
        encoded_attachments = []
        for att in attachments:
            with open(att["file_path"], "rb") as f:
                content = base64.b64encode(f.read()).decode('utf-8')
                encoded_attachments.append({
                    "filename": att["filename"],
                    "content_base64": content
                })
        request_data["params"]["attachments"] = encoded_attachments
    
    response = requests.post(
        MCP_SERVER_URL,
        json=request_data,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()

# 사용 예시
result = send_email_via_mcp(
    recipient_emails=["test@example.com"],
    sender_email="sender@example.com",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",
    subject="Test Email",
    body="This is a test email"
)
print(result)
```

### JavaScript/Node.js 예제

```javascript
const axios = require('axios');
const fs = require('fs');

const MCP_SERVER_URL = 'http://localhost:8102/mcp';

async function sendEmailViaMCP(params) {
  const requestData = {
    method: 'send_email',
    params: {
      recipient_emails: params.recipientEmails,
      sender_email: params.senderEmail,
      smtp_host: params.smtpHost,
      smtp_port: params.smtpPort,
      smtp_username: params.smtpUsername,
      smtp_password: params.smtpPassword,
      use_ssl: true,
      subject: params.subject,
      body: params.body
    }
  };

  if (params.ccEmails) {
    requestData.params.cc_emails = params.ccEmails;
  }
  if (params.bccEmails) {
    requestData.params.bcc_emails = params.bccEmails;
  }
  if (params.attachments) {
    // 파일을 base64로 인코딩
    requestData.params.attachments = params.attachments.map(att => ({
      filename: att.filename,
      content_base64: fs.readFileSync(att.filePath).toString('base64')
    }));
  }

  try {
    const response = await axios.post(MCP_SERVER_URL, requestData, {
      headers: { 'Content-Type': 'application/json' }
    });
    return response.data;
  } catch (error) {
    console.error('Error sending email:', error.response?.data || error.message);
    throw error;
  }
}

// 사용 예시
sendEmailViaMCP({
  recipientEmails: ['test@example.com'],
  senderEmail: 'sender@example.com',
  smtpHost: 'smtp.gmail.com',
  smtpPort: 587,
  smtpUsername: 'your-email@gmail.com',
  smtpPassword: 'your-app-password',
  subject: 'Test Email',
  body: 'This is a test email'
}).then(result => {
  console.log(result);
});
```

### cURL 예제

```bash
# 이메일 발송
curl -X POST http://localhost:8102/mcp \
  -H "Content-Type: application/json" \
  -d '{
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
  }'

# 로그 조회
curl -X POST http://localhost:8102/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "get_email_log",
    "params": {
      "log_id": "027fc027-2da1-44d6-ac75-b5e496eafe47"
    }
  }'

# 로그 목록 조회
curl -X POST http://localhost:8102/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "list_email_logs",
    "params": {
      "skip": 0,
      "limit": 10
    }
  }'
```

## 에러 처리

MCP 서버는 JSON-RPC 스타일의 에러 응답을 반환합니다:

```json
{
  "error": {
    "code": -32602,
    "message": "받는 사람 이메일을 최소 1개 이상 입력해주세요."
  }
}
```

**에러 코드:**
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32700`: Parse error

## 주의사항

1. **포트 변경**: MCP 서버 포트가 변경된 경우 `mcp-client-config.example.json`의 URL을 업데이트하세요.
2. **보안**: 프로덕션 환경에서는 HTTPS를 사용하고 인증을 추가하는 것을 권장합니다.
3. **CORS**: 현재 모든 origin에서 접근 가능하도록 설정되어 있습니다. 프로덕션에서는 특정 도메인만 허용하도록 변경하세요.

