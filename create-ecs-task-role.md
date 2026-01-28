# ecsTaskRole 생성 가이드

## IAM 콘솔에서 역할 생성

### 1단계: 역할 생성
1. IAM 콘솔 → Roles → "역할 생성" (Create Role) 클릭
2. 신뢰할 수 있는 엔터티 유형 선택:
   - **AWS 서비스** 선택
3. 사용 사례 선택:
   - **Elastic Container Service** 검색
   - **Elastic Container Service Task** 선택
   - "다음" 클릭

### 2단계: 권한 추가
1. 정책 연결:
   - 검색: `SecretsManager`
   - **SecretsManagerReadOnly** 또는 **SecretsManagerReadWrite** 선택
   - "다음" 클릭

### 3단계: 역할 이름 지정
1. 역할 이름: `ecsTaskRole`
2. 설명: "ECS Task Role for ig-notification service"
3. "역할 생성" 클릭

## 또는 CLI로 생성

```bash
# 1. Trust Policy 파일 생성
cat > ecs-task-role-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 2. 역할 생성
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document file://ecs-task-role-trust-policy.json \
  --description "ECS Task Role for ig-notification service"

# 3. Secrets Manager 권한 추가
aws iam attach-role-policy \
  --role-name ecsTaskRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

