# EC2 빌드 빠른 시작 가이드

## 현재 상태
- ✅ EC2 인스턴스 준비: `i-08eb9d8a486cf0692` (54.180.116.73)
- ✅ 코드 압축 파일: S3에 업로드됨

## 빠른 시작 (5분)

### 1. AWS 콘솔에서 EC2 Instance Connect

1. AWS 콘솔 → EC2 → Instances
2. `i-08eb9d8a486cf0692` 선택 → **"Connect"** 클릭
3. **"EC2 Instance Connect"** 탭 → **"Connect"** 클릭

### 2. 브라우저 터미널에서 실행

```bash
# S3에서 코드 다운로드
cd ~
aws s3 cp s3://ignite-pilot-s3-1/ig-notification-build.tar.gz . --region ap-northeast-2

# 압축 해제
tar -xzf ig-notification-build.tar.gz
cd ig-notification

# Docker 이미지 빌드 (x86_64)
docker build -f Dockerfile.aws -t ig-notification:latest .

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  575084400422.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그 및 푸시
docker tag ig-notification:latest \
  575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest

docker push 575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest

echo "✅ 완료!"
```

### 3. 로컬에서 ECS Service 업데이트

```bash
aws ecs update-service \
  --cluster aws-deploy-wizard \
  --service ig-notification \
  --force-new-deployment \
  --region ap-northeast-2
```

### 4. 인스턴스 종료 (선택사항)

```bash
aws ec2 terminate-instances \
  --instance-ids i-08eb9d8a486cf0692 \
  --region ap-northeast-2
```

## 예상 시간
- 다운로드: 1분
- 빌드: 5-10분
- 푸시: 2-3분
- **총: 약 10-15분**

