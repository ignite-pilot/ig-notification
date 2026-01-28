# ECS Task Definition 설정 가이드

## 현재 상태
- Task Definition JSON 파일 준비 완료: `ecs-task-definition.json`
- 필요한 권한이 없어 등록 대기 중

## 필요한 AWS 권한

현재 사용자(`dev-pilot-reader`)에게 다음 권한이 필요합니다:

### 1. ECS 권한
- `ecs:RegisterTaskDefinition`
- `ecs:DescribeTaskDefinition`
- `ecs:ListTaskDefinitions`

### 2. IAM PassRole 권한
- `iam:PassRole` (다음 리소스에 대해):
  - `arn:aws:iam::575084400422:role/ecsTaskExecutionRole`
  - `arn:aws:iam::575084400422:role/ecsTaskRole`

### 3. CloudWatch Logs 권한 (선택사항 - 로그 그룹 생성용)
- `logs:CreateLogGroup`
- `logs:DescribeLogGroups`

## 사전 준비 사항

### 1. IAM 역할 확인/생성
다음 IAM 역할이 존재해야 합니다:
- `ecsTaskExecutionRole`: ECS Task 실행 역할 (ECR 이미지 pull, CloudWatch Logs 쓰기 등)
- `ecsTaskRole`: Task 역할 (애플리케이션이 AWS 서비스에 접근할 때 사용)

### 2. CloudWatch Logs 그룹 생성 (선택사항)
```bash
aws logs create-log-group --log-group-name /ecs/ig-notification --region ap-northeast-2
```

### 3. Secrets Manager 확인
다음 Secrets가 존재해야 합니다:
- `prod/ignite-pilot/aws-credentials` (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- `prod/ignite-pilot/ig-notification-api-key` (API_KEY)

## Task Definition 등록 방법

권한이 추가되면 다음 명령으로 등록할 수 있습니다:

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ap-northeast-2
```

또는 AWS 콘솔에서:
1. ECS 콘솔 → Task Definitions → Create new Task Definition
2. JSON 탭 선택
3. `ecs-task-definition.json` 파일 내용 복사/붙여넣기
4. Create

## Task Definition 정보

- **Family**: `ig-notification`
- **Network Mode**: `awsvpc`
- **Launch Type**: `FARGATE`
- **CPU**: 512 (0.5 vCPU)
- **Memory**: 1024 MB (1 GB)
- **Container Port**: 80
- **Health Check**: `http://127.0.0.1:80/api/health`

