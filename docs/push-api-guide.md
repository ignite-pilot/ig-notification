# FCM 푸시 알림 API 연동 가이드

외부 시스템에서 IG Notification 서비스를 통해 FCM 푸시 알림을 발송하는 방법을 안내합니다.

## 목차

- [개요](#개요)
- [사전 준비](#사전-준비)
- [인증](#인증)
- [API 엔드포인트](#api-엔드포인트)
  - [푸시 발송](#1-푸시-발송)
  - [발송 로그 목록 조회](#2-발송-로그-목록-조회)
  - [발송 로그 상세 조회](#3-발송-로그-상세-조회)
- [응답 코드](#응답-코드)
- [연동 예제](#연동-예제)
- [AWS Secrets Manager 설정](#aws-secrets-manager-설정)
- [주의사항 및 제한](#주의사항-및-제한)

---

## 개요

| 항목 | 내용 |
|------|------|
| 기본 URL | `https://ig-notification.ig-pilot.com` |
| 프로토콜 | HTTPS |
| 요청 형식 | `multipart/form-data` |
| 응답 형식 | `application/json` |
| Rate Limit | 분당 10회 (IP 기준) |

---

## 사전 준비

### 1. Firebase 프로젝트 설정

푸시 알림을 발송하려면 Firebase 프로젝트가 필요합니다.

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. **프로젝트 설정 > 서비스 계정** 탭 이동
3. **새 비공개 키 생성** 클릭 → `serviceAccountKey.json` 다운로드
4. 다운로드한 JSON 파일을 AWS Secrets Manager에 등록 (아래 [AWS Secrets Manager 설정](#aws-secrets-manager-설정) 참고)

### 2. Firebase 프로젝트 ID 확인

`serviceAccountKey.json`의 `project_id` 값 또는 Firebase Console > 프로젝트 설정 > 일반 탭에서 확인합니다.

```json
{
  "type": "service_account",
  "project_id": "your-firebase-project-id",
  ...
}
```

### 3. FCM 디바이스 토큰 수집

클라이언트 앱(Android/iOS)에서 FCM 디바이스 토큰을 발급받아 서버에 저장해야 합니다.

**Android (Kotlin) 예시:**
```kotlin
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (task.isSuccessful) {
        val token = task.result
        // 서버에 토큰 저장
    }
}
```

---

## 인증

API 키가 설정된 환경에서는 모든 발송 요청에 `X-API-Key` 헤더가 필요합니다.

```http
X-API-Key: your-api-key
```

> **참고:** 로그 조회 API는 API 키 없이도 사용 가능합니다.

---

## API 엔드포인트

### 1. 푸시 발송

```
POST /api/v1/push/send
Content-Type: multipart/form-data
X-API-Key: your-api-key
```

#### 요청 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `firebase_project_id` | string | ✅ | Firebase 프로젝트 ID |
| `device_tokens` | string (JSON 배열) | ✅ | 디바이스 토큰 목록 (최대 500개) |
| `title` | string | ✅ | 알림 제목 |
| `body` | string | ✅ | 알림 내용 |
| `data` | string (JSON 객체) | ❌ | 추가 데이터 (모든 값은 문자열) |

#### 요청 예시

```bash
curl -X POST https://ig-notification.ig-pilot.com/api/v1/push/send \
  -H "X-API-Key: your-api-key" \
  -F "firebase_project_id=your-firebase-project-id" \
  -F 'device_tokens=["token1", "token2", "token3"]' \
  -F "title=새 알림" \
  -F "body=확인해주세요." \
  -F 'data={"screen": "home", "id": "123"}'
```

#### 응답 예시

**성공 (200 OK):**
```json
{
  "logId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "message": "푸시 알림이 성공적으로 발송되었습니다. (성공: 3, 실패: 0)",
  "successCount": 3,
  "failureCount": 0,
  "createdAt": "2026-04-08T10:00:00"
}
```

**부분 실패 (200 OK, status: partial):**
```json
{
  "logId": "550e8400-e29b-41d4-a716-446655440001",
  "status": "partial",
  "message": "푸시 알림이 성공적으로 발송되었습니다. (성공: 2, 실패: 1)",
  "successCount": 2,
  "failureCount": 1,
  "createdAt": "2026-04-08T10:00:00"
}
```

**발송 실패 (200 OK, status: failed):**
```json
{
  "logId": "550e8400-e29b-41d4-a716-446655440002",
  "status": "failed",
  "message": "푸시 알림 발송 실패: Secret 'prod/ignite-pilot/your-project-android-key'을 찾을 수 없습니다.",
  "successCount": 0,
  "failureCount": 1,
  "createdAt": "2026-04-08T10:00:00"
}
```

#### status 값 설명

| status | 의미 |
|--------|------|
| `success` | 모든 토큰 발송 성공 |
| `partial` | 일부 토큰만 발송 성공 |
| `failed` | 전체 발송 실패 |

---

### 2. 발송 로그 목록 조회

```
GET /api/v1/push/logs?skip=0&limit=100
```

#### 쿼리 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `skip` | integer | 0 | 건너뛸 항목 수 (페이지네이션) |
| `limit` | integer | 100 | 조회할 최대 항목 수 |

#### 응답 예시

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "firebase_project_id": "your-firebase-project-id",
    "title": "새 알림",
    "body": "확인해주세요.",
    "data": {"screen": "home", "id": "123"},
    "device_tokens": ["token1", "token2"],
    "success_count": 2,
    "failure_count": 0,
    "failed_tokens": null,
    "status": "success",
    "error_message": null,
    "created_at": "2026-04-08T10:00:00",
    "sent_at": "2026-04-08T10:00:01"
  }
]
```

---

### 3. 발송 로그 상세 조회

```
GET /api/v1/push/logs/{log_id}
```

#### 경로 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `log_id` | UUID string | 발송 로그 ID (`logId` 값) |

#### 응답 예시

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "firebase_project_id": "your-firebase-project-id",
  "title": "새 알림",
  "body": "확인해주세요.",
  "data": {"screen": "home", "id": "123"},
  "device_tokens": ["token1", "token2"],
  "success_count": 2,
  "failure_count": 0,
  "failed_tokens": null,
  "status": "success",
  "error_message": null,
  "created_at": "2026-04-08T10:00:00",
  "sent_at": "2026-04-08T10:00:01"
}
```

---

## 응답 코드

| HTTP 코드 | 의미 |
|-----------|------|
| `200` | 요청 처리 완료 (발송 실패도 200으로 응답, `status` 필드로 구분) |
| `400` | 잘못된 요청 (파라미터 오류, 유효성 검증 실패) |
| `401` | API 키 없음 또는 유효하지 않음 |
| `404` | 로그를 찾을 수 없음 |
| `422` | 요청 형식 오류 |
| `429` | Rate Limit 초과 (분당 10회) |
| `500` | 서버 오류 |

---

## 연동 예제

### Python

```python
import requests

API_BASE_URL = "https://ig-notification.ig-pilot.com"
API_KEY = "your-api-key"

def send_push(firebase_project_id, device_tokens, title, body, data=None):
    response = requests.post(
        f"{API_BASE_URL}/api/v1/push/send",
        headers={"X-API-Key": API_KEY},
        data={
            "firebase_project_id": firebase_project_id,
            "device_tokens": json.dumps(device_tokens),
            "title": title,
            "body": body,
            "data": json.dumps(data) if data else None,
        }
    )
    return response.json()

# 사용 예시
import json

result = send_push(
    firebase_project_id="your-firebase-project-id",
    device_tokens=["device_token_1", "device_token_2"],
    title="새 메시지",
    body="홍길동님이 메시지를 보냈습니다.",
    data={"screen": "chat", "roomId": "456"}
)
print(result)
```

### JavaScript (fetch)

```javascript
async function sendPush({ firebaseProjectId, deviceTokens, title, body, data }) {
  const formData = new FormData();
  formData.append("firebase_project_id", firebaseProjectId);
  formData.append("device_tokens", JSON.stringify(deviceTokens));
  formData.append("title", title);
  formData.append("body", body);
  if (data) formData.append("data", JSON.stringify(data));

  const response = await fetch("https://ig-notification.ig-pilot.com/api/v1/push/send", {
    method: "POST",
    headers: { "X-API-Key": "your-api-key" },
    body: formData,
  });

  return response.json();
}

// 사용 예시
const result = await sendPush({
  firebaseProjectId: "your-firebase-project-id",
  deviceTokens: ["device_token_1", "device_token_2"],
  title: "새 알림",
  body: "확인해주세요.",
  data: { screen: "home" },
});
console.log(result);
```

### Kotlin (Android)

```kotlin
import okhttp3.*
import org.json.JSONObject
import org.json.JSONArray

fun sendPush(
    firebaseProjectId: String,
    deviceTokens: List<String>,
    title: String,
    body: String,
    data: Map<String, String>? = null
) {
    val client = OkHttpClient()

    val formBuilder = MultipartBody.Builder().setType(MultipartBody.FORM)
        .addFormDataPart("firebase_project_id", firebaseProjectId)
        .addFormDataPart("device_tokens", JSONArray(deviceTokens).toString())
        .addFormDataPart("title", title)
        .addFormDataPart("body", body)

    data?.let { formBuilder.addFormDataPart("data", JSONObject(it).toString()) }

    val request = Request.Builder()
        .url("https://ig-notification.ig-pilot.com/api/v1/push/send")
        .addHeader("X-API-Key", "your-api-key")
        .post(formBuilder.build())
        .build()

    client.newCall(request).execute().use { response ->
        val responseBody = response.body?.string()
        println(responseBody)
    }
}
```

---

## AWS Secrets Manager 설정

IG Notification 서비스는 Firebase 서비스 계정 키를 AWS Secrets Manager에서 자동으로 조회합니다.

### Secret 이름 규칙

```
prod/ignite-pilot/{firebase_project_id}-android-key
```

예시: Firebase 프로젝트 ID가 `reborn`이라면 → `prod/ignite-pilot/reborn-android-key`

### 등록 방법

1. Firebase Console에서 다운로드한 `serviceAccountKey.json` 내용을 그대로 등록

```bash
aws secretsmanager create-secret \
  --name "prod/ignite-pilot/your-project-android-key" \
  --region ap-northeast-2 \
  --secret-string file://serviceAccountKey.json
```

### Secret 형식

```json
{
  "type": "service_account",
  "project_id": "your-firebase-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
  "client_email": "firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

> Secret의 `type` 필드가 반드시 `"service_account"` 이어야 합니다.

---

## 주의사항 및 제한

| 항목 | 제한 |
|------|------|
| 디바이스 토큰 | 요청당 최대 **500개** |
| Rate Limit | IP당 분당 **10회** |
| `data` 값 타입 | 모든 값이 **문자열**이어야 함 (`"123"` O, `123` X) |
| 토큰 유효성 | 만료된 토큰은 `failureCount`에 반영되며 `failed_tokens`에 기록 |

### 만료된 토큰 처리

`failureCount > 0`인 경우 로그 상세 조회로 `failed_tokens` 목록을 확인하고, 해당 토큰을 DB에서 제거하는 것을 권장합니다.

```python
result = send_push(...)
if result["failureCount"] > 0:
    log = get_push_log(result["logId"])
    # failed_tokens를 DB에서 제거
    remove_invalid_tokens(log["failed_tokens"])
```
