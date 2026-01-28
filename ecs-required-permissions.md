# ECS Task Definition 등록 및 실행에 필요한 권한

## 현재 상태
- Task Definition JSON 파일 준비 완료: `ecs-task-definition.json`
- 등록 실패: IAM PassRole 권한 부족

## 필요한 권한 (현재 사용자: dev-pilot-reader)

### 1. ECS Task Definition 등록 권한

현재 사용자(`dev-pilot-reader`)에게 다음 권한이 필요합니다:

#### ECS 권한
- `ecs:RegisterTaskDefinition`
- `ecs:DescribeTaskDefinition`
- `ecs:ListTaskDefinitions`

#### IAM PassRole 권한 (필수)
- `iam:PassRole` (다음 리소스에 대해):
  - `arn:aws:iam::575084400422:role/ecsTaskExecutionRole`
  - `arn:aws:iam::575084400422:role/ecsTaskRole`

**참고**: PowerUserAccess에는 IAM PassRole 권한이 포함되지 않으므로 별도로 추가해야 합니다.

### 2. IAM 역할 권한 (ecsTaskRole)

Task Definition에서 사용하는 `ecsTaskRole`에 다음 권한이 필요합니다:

#### Secrets Manager 읽기 권한
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:ap-northeast-2:575084400422:secret:prod/ignite-pilot/postgresInfo2*"
      ]
    }
  ]
}
```

**AWS 관리형 정책 사용 가능**:
- `SecretsManagerReadWrite` (읽기/쓰기)
- 또는 `SecretsManagerReadOnly` (읽기 전용, 권장)

### 3. IAM 역할 권한 (ecsTaskExecutionRole)

Task Definition에서 사용하는 `ecsTaskExecutionRole`에 다음 권한이 필요합니다:

#### ECR 이미지 Pull 권한
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`

**AWS 관리형 정책**: `AmazonECSTaskExecutionRolePolicy` (이미 포함되어 있을 가능성 높음)

#### CloudWatch Logs 쓰기 권한
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `logs:CreateLogGroup` (선택사항 - 로그 그룹이 없을 경우)

**AWS 관리형 정책**: `CloudWatchLogsFullAccess` 또는 `AmazonECSTaskExecutionRolePolicy`에 포함

## 해결 방법

### 방법 1: IAM 관리자에게 권한 요청 (권장)

현재 사용자(`dev-pilot-reader`)에게 다음 정책을 추가 요청:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:RegisterTaskDefinition",
        "ecs:DescribeTaskDefinition",
        "ecs:ListTaskDefinitions"
      ],
      "Resource": "*"
    },
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

### 방법 2: AWS 콘솔에서 등록

콘솔에서는 다른 권한 체크가 있을 수 있으므로 시도해볼 수 있습니다:
1. ECS 콘솔 → Task Definitions → Create new Task Definition
2. JSON 탭 선택
3. `ecs-task-definition.json` 파일 내용 복사/붙여넣기
4. Create

### 방법 3: Task Role 제거 (제한적)

`taskRoleArn`을 제거하면 PassRole 권한이 하나 줄어들지만, Secrets Manager 접근이 안 될 수 있습니다.

## 사전 확인 사항

### IAM 역할 존재 확인
- `ecsTaskExecutionRole`: 존재해야 함 (ECR pull, CloudWatch Logs)
- `ecsTaskRole`: 존재해야 함 (Secrets Manager 접근)

### Secrets Manager Secret 확인
- `prod/ignite-pilot/postgresInfo2`: 존재해야 함

### CloudWatch Logs 그룹
- `/ecs/ig-notification`: 없으면 자동 생성됨 (ecsTaskExecutionRole에 권한이 있으면)

## Task Definition 등록 명령어

권한이 추가되면 다음 명령으로 등록:

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ap-northeast-2
```

