# IAM 콘솔에서 추가할 정책 이름

## 현재 화면: dev-pilot-reader 사용자 권한 추가

### 검색해서 찾을 정책 이름

#### 1. ECS 권한 (필수)
**검색어**: `ECS` 또는 `AmazonECS`

**추천 정책**:
- `AmazonECS_FullAccess` ✅ (권장)
  - ECS 관련 모든 권한 포함
  - Task Definition 등록, Service 생성 등 모든 ECS 작업 가능

**대안** (더 제한적인 권한 원하는 경우):
- `AmazonECS_ReadOnlyAccess` (읽기 전용)
- 하지만 Task Definition 등록에는 FullAccess 필요

---

#### 2. IAM PassRole 권한 (필수 - 커스텀 정책 필요)

⚠️ **중요**: IAM PassRole 권한은 AWS 관리형 정책이 **없습니다**.

**해결 방법**:
1. **커스텀 정책 생성 필요**
   - IAM 콘솔 → Policies → Create policy
   - JSON 탭 선택
   - 아래 정책 내용 복사/붙여넣기

**커스텀 정책 내용**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": [
        "arn:aws:iam::575084400422:role/ecsTaskExecutionRole",
        "arn:aws:iam::575084400422:role/ecsTaskRole"
      ]
    }
  ]
}
```

**정책 이름**: `ECSTaskDefinitionPassRolePolicy` (또는 원하는 이름)

2. 정책 생성 후 이 화면에서 검색하여 연결

---

## 추가 단계 (별도 작업)

### ecsTaskRole에 Secrets Manager 권한 추가

이것은 `dev-pilot-reader` 사용자가 아니라 `ecsTaskRole` IAM 역할에 추가해야 합니다.

**위치**: IAM 콘솔 → Roles → `ecsTaskRole` → Add permissions

**검색어**: `SecretsManager` 또는 `Secrets`

**추천 정책**:
- `SecretsManagerReadWrite` (읽기/쓰기)
- 또는 `SecretsManagerReadOnly` (읽기 전용, 권장)

---

## 요약: 화면에서 할 일

### 1단계: ECS 권한 추가
- 검색: `ECS` 또는 `AmazonECS`
- 선택: `AmazonECS_FullAccess`
- 연결

### 2단계: IAM PassRole 권한 추가
- 먼저 커스텀 정책 생성 (위 정책 내용 사용)
- 그 다음 이 화면에서 생성한 정책 검색
- 연결

### 3단계: (별도) ecsTaskRole에 Secrets Manager 권한 추가
- IAM 콘솔 → Roles → `ecsTaskRole`로 이동
- 검색: `SecretsManager`
- 선택: `SecretsManagerReadOnly` 또는 `SecretsManagerReadWrite`
- 연결

