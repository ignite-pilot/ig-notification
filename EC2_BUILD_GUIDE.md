# EC2에서 Docker 이미지 빌드 가이드

## 현재 상태
- ✅ EC2 인스턴스 생성 완료
- ✅ Instance ID: `i-08eb9d8a486cf0692`
- ✅ Public IP: `54.180.116.73`
- ✅ SSH 포트 22 열림

## 가장 간단한 방법: AWS 콘솔 EC2 Instance Connect 사용

### 1단계: AWS 콘솔에서 연결
1. AWS 콘솔 → EC2 → Instances
2. 인스턴스 `i-08eb9d8a486cf0692` 선택
3. "Connect" 버튼 클릭
4. "EC2 Instance Connect" 탭 선택
5. "Connect" 클릭

### 2단계: 브라우저 터미널에서 실행

연결된 터미널에서 다음 명령어 실행:

```bash
# 프로젝트 클론
cd ~
git clone https://github.com/ignite-pilot/ig-notification.git
cd ig-notification

# 또는 코드 전송 (아래 방법 사용)
```

## 방법 2: 코드를 직접 전송

### 로컬에서 코드 압축 및 전송

로컬 터미널에서:

```bash
cd /Users/ignite/Documents/AI\ Coding/cursor_project
tar -czf ig-notification-build.tar.gz ig-notification \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='frontend/dist' \
  --exclude='*.pyc' \
  --exclude='__pycache__'

# AWS 콘솔의 EC2 Instance Connect에서 파일 업로드 기능 사용
# 또는 S3에 업로드 후 EC2에서 다운로드
```

### EC2에서 압축 해제 및 빌드

EC2 Instance Connect 터미널에서:

```bash
# 파일이 업로드되었다면
cd ~
tar -xzf ig-notification-build.tar.gz
cd ig-notification

# 또는 S3에서 다운로드
# aws s3 cp s3://your-bucket/ig-notification-build.tar.gz ~/
# tar -xzf ig-notification-build.tar.gz
# cd ig-notification
```

## 빌드 및 푸시

EC2 인스턴스에서 다음 명령어 실행:

```bash
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

echo "✅ 빌드 및 푸시 완료!"
```

## 빌드 완료 후

### ECS Service 업데이트 확인
```bash
# 로컬에서 실행
aws ecs update-service \
  --cluster aws-deploy-wizard \
  --service ig-notification \
  --force-new-deployment \
  --region ap-northeast-2
```

### EC2 인스턴스 종료 (비용 절감)
```bash
aws ec2 terminate-instances \
  --instance-ids i-08eb9d8a486cf0692 \
  --region ap-northeast-2
```

## 문제 해결

### Docker가 설치되지 않은 경우
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu
newgrp docker  # 그룹 변경 적용
```

### AWS CLI가 설치되지 않은 경우
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Git clone이 안 되는 경우
- GitHub 저장소가 private인 경우: Personal Access Token 필요
- 또는 코드를 직접 전송하는 방법 사용

