# x86_64 아키텍처로 Docker 이미지 재빌드 가이드

## 문제
- 현재 이미지가 ARM64로 빌드되어 ECS Fargate(x86_64)에서 실행되지 않음
- 로그에 "exec format error" 발생

## 해결 방법

### 옵션 1: GitHub Actions 사용 (권장)

GitHub Actions에서 x86_64로 빌드하고 ECR에 푸시:

```yaml
# .github/workflows/build-and-push.yml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ig-notification
          IMAGE_TAG: latest
        run: |
          docker build -f Dockerfile.aws -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

### 옵션 2: AWS CodeBuild 사용

AWS CodeBuild에서 x86_64로 빌드

### 옵션 3: 로컬에서 Docker Desktop의 BuildKit 사용

Docker Desktop이 설치되어 있다면:

```bash
# BuildKit 활성화
export DOCKER_BUILDKIT=1

# x86_64로 빌드
docker build --platform linux/amd64 -f Dockerfile.aws -t ig-notification:latest .
```

### 옵션 4: EC2 인스턴스에서 빌드

x86_64 EC2 인스턴스에서 빌드 후 ECR에 푸시

## 현재 수정된 내용

1. ✅ `backend/main.py`: 컨테이너에서 항상 `0.0.0.0` 사용하도록 수정
2. ✅ `Dockerfile.aws`: EXPOSE 포트를 80으로 변경
3. ✅ Health check 경로 수정

## 다음 단계

x86_64로 이미지를 재빌드하고 ECR에 푸시한 후:
1. ECS Service가 자동으로 새 이미지를 pull
2. Task가 정상적으로 시작됨
3. Health Check 통과
4. 서비스 접근 가능

