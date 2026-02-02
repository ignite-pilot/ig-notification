# ECS 배포 완료 요약

## 배포 완료 항목

### ✅ 1. Docker 이미지
- **ECR Repository**: `ig-notification`
- **Image URI**: `575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest`
- **Status**: 푸시 완료

### ✅ 2. Task Definition
- **Family**: `ig-notification`
- **Revision**: `1`
- **ARN**: `arn:aws:ecs:ap-northeast-2:575084400422:task-definition/ig-notification:1`
- **Status**: `ACTIVE`
- **CPU**: 512 (0.5 vCPU)
- **Memory**: 1024 MB (1 GB)
- **Container Port**: 80

### ✅ 3. ECS Service
- **Service Name**: `ig-notification`
- **Cluster**: `aws-deploy-wizard`
- **Status**: `ACTIVE`
- **Desired Count**: `1`
- **Capacity Provider**: `FARGATE_SPOT`

### ✅ 4. Target Group
- **Name**: `ig-notification-tg`
- **ARN**: `arn:aws:elasticloadbalancing:ap-northeast-2:575084400422:targetgroup/ig-notification-tg/6d9d7c6270af9ead`
- **Port**: 80
- **Protocol**: HTTP
- **Health Check Path**: `/api/health`
- **Health Check Protocol**: HTTP

### ✅ 5. ALB 라우팅
- **ALB Name**: `memo-test1-alb`
- **ALB DNS**: `memo-test1-alb-871676467.ap-northeast-2.elb.amazonaws.com`
- **Listener**: HTTPS (443)
- **SSL Certificate**: 설정됨
- **Routing Rule**: `ig-notification.ignite-pilot.com` → `ig-notification-tg`

## 도메인 설정

### 도메인: `ig-notification.ignite-pilot.com`

**DNS 설정 필요**:
- **Type**: A (또는 CNAME)
- **Name**: `ig-notification.ignite-pilot.com`
- **Value**: `memo-test1-alb-871676467.ap-northeast-2.elb.amazonaws.com`

또는 Route53을 사용하는 경우:
```bash
# Route53에서 호스트 영역 확인 후 레코드 생성
aws route53 change-resource-record-sets --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "ig-notification.ignite-pilot.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "KZWEBALFJHHDQ",
          "DNSName": "memo-test1-alb-871676467.ap-northeast-2.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

## 확인 사항

### 1. Task 실행 확인
```bash
aws ecs list-tasks --cluster aws-deploy-wizard --service-name ig-notification --region ap-northeast-2
```

### 2. Task 상태 확인
```bash
aws ecs describe-tasks --cluster aws-deploy-wizard --tasks <task-arn> --region ap-northeast-2
```

### 3. Health Check 확인
- Target Group Health: ALB 콘솔에서 확인
- Health Check Path: `/api/health`

### 4. Secrets Manager 권한 확인
- `ecsTaskRole`에 `SecretsManagerReadOnly` 또는 `SecretsManagerReadWrite` 권한이 있는지 확인
- Secret: `prod/ignite-pilot/mysql-realpilot`

## 접근 방법

### HTTPS 접근
- **URL**: `https://ig-notification.ignite-pilot.com`
- **ALB**: HTTPS (443) → HTTP (80)로 전달
- **Health Check**: `https://ig-notification.ignite-pilot.com/api/health`

### HTTP 접근 (리다이렉트)
- **URL**: `http://ig-notification.ignite-pilot.com`
- **ALB**: HTTP (80) → HTTPS (443)로 리다이렉트

## 다음 단계

1. ✅ DNS 설정 완료 (Route53 또는 DNS 제공자)
2. ⏳ Task 시작 대기 (몇 분 소요)
3. ⏳ Health Check 통과 확인
4. ⏳ 서비스 접근 테스트

## 문제 해결

### Task가 시작되지 않는 경우
- CloudWatch Logs 확인: `/ecs/ig-notification`
- Task Definition의 환경 변수 확인
- Secrets Manager 권한 확인
- Security Group 규칙 확인

### Health Check 실패
- 애플리케이션이 80 포트에서 실행 중인지 확인
- `/api/health` 엔드포인트가 정상 동작하는지 확인
- Security Group에서 ALB → ECS 트래픽 허용 확인

