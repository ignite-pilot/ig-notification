# AmazonECS_FullAccess 권한 분석

## AmazonECS_FullAccess가 포함하는 권한

### ✅ 포함되는 권한
- ECS 관련 모든 권한 (RegisterTaskDefinition, CreateService, UpdateService 등)
- VPC, Auto Scaling, CloudFormation 등 관련 서비스 접근
- ECR 이미지 접근 (일부)

### ❌ 포함되지 않는 권한

#### 1. IAM PassRole 권한
- `iam:PassRole` 권한은 **포함되지 않음**
- 이유: 보안상의 이유로 AWS 관리형 정책에는 IAM 권한이 제한적으로 포함됨
- **결과**: Task Definition 등록 시 여전히 PassRole 권한 오류 발생

#### 2. Secrets Manager 권한
- `secretsmanager:GetSecretValue` 권한은 **포함되지 않음**
- **결과**: 애플리케이션이 Secrets Manager에서 DB 정보를 읽을 수 없음

## 해결 방법

### 옵션 1: AmazonECS_FullAccess + 추가 권한 (권장)

#### 현재 사용자 (`dev-pilot-reader`)에 추가 필요:
1. **IAM PassRole 권한** (커스텀 정책 필요)
   ```json
   {
     "Effect": "Allow",
     "Action": "iam:PassRole",
     "Resource": [
       "arn:aws:iam::575084400422:role/ecsTaskExecutionRole",
       "arn:aws:iam::575084400422:role/ecsTaskRole"
     ]
   }
   ```

#### `ecsTaskRole`에 추가 필요:
2. **Secrets Manager 읽기 권한**
   - AWS 관리형 정책: `SecretsManagerReadOnly` 또는 `SecretsManagerReadWrite`
   - 또는 커스텀 정책 (ecs-task-role-policy.json 참고)

### 옵션 2: AWS 콘솔 사용
- 콘솔에서는 다른 권한 체크가 있을 수 있으므로 시도 가능
- 하지만 실행 시 Secrets Manager 접근 오류 발생 가능

## 결론

**`AmazonECS_FullAccess`만으로는 해결되지 않습니다.**

필요한 추가 권한:
1. ✅ ECS 권한: `AmazonECS_FullAccess`로 해결
2. ❌ IAM PassRole: 별도 추가 필요
3. ❌ Secrets Manager: `ecsTaskRole`에 별도 추가 필요

