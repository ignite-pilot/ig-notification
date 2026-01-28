# EC2에서 수동으로 빌드하는 방법

## EC2 인스턴스 정보
- **Instance ID**: `i-08eb9d8a486cf0692`
- **Public IP**: `54.180.116.73`
- **Key Pair**: `ig-pilot`

## SSH 연결

### 1. 키 파일 위치 확인
키 파일이 `~/.ssh/ig-pilot.pem`에 있어야 합니다. 없다면:
- AWS 콘솔에서 키 페어 다운로드
- 또는 기존 키 파일 경로 사용

### 2. SSH 연결
```bash
ssh -i ~/.ssh/ig-pilot.pem ubuntu@54.180.116.73
```

### 3. 인스턴스에서 실행할 명령어

인스턴스에 SSH로 연결한 후 다음 명령어를 실행:

```bash
# 프로젝트 클론
cd ~
git clone https://github.com/ignite-pilot/ig-notification.git
cd ig-notification

# 또는 코드를 직접 전송하는 경우
# scp -r -i ~/.ssh/ig-pilot.pem /path/to/ig-notification ubuntu@54.180.116.73:~/

# Docker 이미지 빌드
docker build -f Dockerfile.aws -t ig-notification:latest .

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 575084400422.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그 및 푸시
docker tag ig-notification:latest 575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest
docker push 575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification:latest

echo "✅ 빌드 및 푸시 완료!"
```

## 보안 그룹 확인

SSH 연결이 안 되면 보안 그룹에서 포트 22가 열려있는지 확인:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-06ce21d40d4c0d090 \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region ap-northeast-2
```

## 빌드 완료 후

빌드가 완료되면 인스턴스를 종료:
```bash
aws ec2 terminate-instances --instance-ids i-08eb9d8a486cf0692 --region ap-northeast-2
```

