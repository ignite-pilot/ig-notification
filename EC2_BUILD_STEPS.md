# EC2에서 빌드하는 단계별 가이드

## 현재 준비 완료
- ✅ EC2 인스턴스: `i-08eb9d8a486cf0692` (Public IP: `54.180.116.73`)
- ✅ 코드 압축 파일: `ig-notification-build.tar.gz` (63MB)
- ✅ SSH 포트 22 열림

## 가장 간단한 방법: AWS 콘솔 사용

### 1단계: AWS 콘솔에서 EC2 Instance Connect

1. AWS 콘솔 → EC2 → Instances
2. 인스턴스 `i-08eb9d8a486cf0692` 선택
3. **"Connect"** 버튼 클릭
4. **"EC2 Instance Connect"** 탭 선택
5. **"Connect"** 클릭

브라우저에서 터미널이 열립니다.

### 2단계: 코드 전송 방법 선택

#### 방법 A: Git Clone (저장소가 public인 경우)
```bash
cd ~
git clone https://github.com/ignite-pilot/ig-notification.git
cd ig-notification
```

#### 방법 B: 파일 직접 업로드
1. EC2 Instance Connect 터미널에서:
   ```bash
   cd ~
   ```
2. 브라우저에서 파일 업로드 기능 사용 (EC2 Instance Connect UI에서 제공)
   - 또는 SCP 사용 (로컬에서):
     ```bash
     scp -i ~/.ssh/ig-pilot.pem \
       /Users/ignite/Documents/AI\ Coding/cursor_project/ig-notification-build.tar.gz \
       ubuntu@54.180.116.73:~/
     ```
3. EC2에서 압축 해제:
   ```bash
   tar -xzf ig-notification-build.tar.gz
   cd ig-notification
   ```

### 3단계: 빌드 및 푸시

EC2 터미널에서 실행:

```bash
# Docker 이미지 빌드
docker build -f Dockerfile.aws -t ig-notification:latest .

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  575084400422.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그 및 푸시
docker tag ig-notification:latest \
  575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest

docker push 575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest

echo "✅ 빌드 및 푸시 완료!"
```

### 4단계: ECS Service 업데이트

로컬에서 실행:

```bash
aws ecs update-service \
  --cluster aws-deploy-wizard \
  --service ig-notification \
  --force-new-deployment \
  --region ap-northeast-2
```

### 5단계: EC2 인스턴스 종료 (비용 절감)

```bash
aws ec2 terminate-instances \
  --instance-ids i-08eb9d8a486cf0692 \
  --region ap-northeast-2
```

## 예상 소요 시간
- 빌드: 약 5-10분
- 푸시: 약 2-3분
- 총: 약 10-15분

## 문제 해결

### Docker 명령어가 안 되는 경우
```bash
sudo usermod -aG docker ubuntu
newgrp docker
```

### AWS CLI가 없는 경우
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

