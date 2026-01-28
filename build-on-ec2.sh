#!/bin/bash
# EC2 인스턴스에서 x86_64 Docker 이미지 빌드 및 푸시 스크립트

set -e

AWS_REGION="ap-northeast-2"
ECR_REPOSITORY="ig-notification"
IMAGE_TAG="${1:-latest}"
AWS_ACCOUNT_ID="575084400422"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "=========================================="
echo "EC2에서 Docker 이미지 빌드 및 푸시"
echo "=========================================="
echo ""

# EC2 인스턴스 정보 입력
read -p "EC2 인스턴스 Public IP 또는 Hostname을 입력하세요: " EC2_HOST
read -p "EC2 인스턴스 사용자명 (기본값: ubuntu 또는 ec2-user): " EC2_USER
EC2_USER=${EC2_USER:-ubuntu}

echo ""
echo "EC2 인스턴스에 연결 중: ${EC2_USER}@${EC2_HOST}"
echo ""

# EC2에 필요한 패키지 설치 및 빌드
ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
set -e

echo "=== 시스템 업데이트 및 Docker 설치 확인 ==="
sudo apt-get update -qq
if ! command -v docker &> /dev/null; then
    echo "Docker 설치 중..."
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "Docker 설치 완료"
else
    echo "Docker가 이미 설치되어 있습니다."
fi

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo "AWS CLI 설치 중..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    echo "AWS CLI 설치 완료"
else
    echo "AWS CLI가 이미 설치되어 있습니다."
fi

# Git 설치 확인
if ! command -v git &> /dev/null; then
    echo "Git 설치 중..."
    sudo apt-get install -y git
fi

echo ""
echo "=== 프로젝트 클론 또는 업데이트 ==="
if [ -d "ig-notification" ]; then
    echo "기존 프로젝트 디렉토리 발견, 업데이트 중..."
    cd ig-notification
    git pull || echo "Git pull 실패, 계속 진행..."
else
    echo "프로젝트 클론 중..."
    git clone https://github.com/ignite-pilot/ig-notification.git || {
        echo "Git clone 실패. 수동으로 코드를 전송해야 합니다."
        exit 1
    }
    cd ig-notification
fi

echo ""
echo "=== Docker 이미지 빌드 (x86_64) ==="
docker build -f Dockerfile.aws -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

echo ""
echo "=== ECR 로그인 ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo ""
echo "=== 이미지 태그 및 푸시 ==="
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
docker push ${ECR_URI}:${IMAGE_TAG}

echo ""
echo "✅ 이미지 빌드 및 푸시 완료!"
echo "이미지 URI: ${ECR_URI}:${IMAGE_TAG}"
ENDSSH

echo ""
echo "=========================================="
echo "빌드 및 푸시 완료!"
echo "=========================================="

