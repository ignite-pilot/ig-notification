# EC2에서 Docker 이미지 빌드 가이드

## 현재 상태
- ✅ EC2 인스턴스 생성 완료
- ✅ 인스턴스 ID: `i-08eb9d8a486cf0692`
- ✅ Public IP: `54.180.116.73`
- ⚠️ SSH 연결 필요 (키 파일 경로 확인 필요)

## 방법 1: SSH로 직접 연결하여 빌드

### 1단계: SSH 키 파일 확인
키 파일이 다음 위치에 있어야 합니다:
- `~/.ssh/ig-pilot.pem`
- 또는 다른 경로에 있다면 경로 확인

### 2단계: SSH 연결
```bash
ssh -i ~/.ssh/ig-pilot.pem ubuntu@54.180.116.73
```

### 3단계: 인스턴스에서 빌드 실행

SSH로 연결한 후 다음 명령어 실행:

```bash
# 프로젝트 클론
cd ~
git clone https://github.com/ignite-pilot/ig-notification.git
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

echo "✅ 빌드 및 푸시 완료!"
```

## 방법 2: 코드를 직접 전송

로컬에서 코드를 압축하여 전송:

```bash
# 로컬에서
cd /Users/ignite/Documents/AI\ Coding/cursor_project
tar -czf ig-notification.tar.gz ig-notification --exclude='node_modules' --exclude='venv' --exclude='.git'

# EC2로 전송
scp -i ~/.ssh/ig-pilot.pem ig-notification.tar.gz ubuntu@54.180.116.73:~/

# EC2에서
ssh -i ~/.ssh/ig-pilot.pem ubuntu@54.180.116.73
tar -xzf ig-notification.tar.gz
cd ig-notification
docker build -f Dockerfile.aws -t ig-notification:latest .
# ... (나머지는 위와 동일)
```

## 빌드 완료 후

### ECS Service 업데이트
이미지가 푸시되면 ECS Service가 자동으로 새 이미지를 사용합니다:

```bash
# 강제 재배포 (선택사항)
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

### SSH 연결이 안 되는 경우
1. 보안 그룹에서 포트 22 확인
2. 키 파일 권한 확인: `chmod 400 ~/.ssh/ig-pilot.pem`
3. 인스턴스가 완전히 시작될 때까지 대기 (2-3분)

### Docker가 설치되지 않은 경우
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu
# 로그아웃 후 다시 로그인
```

### AWS CLI가 설치되지 않은 경우
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

