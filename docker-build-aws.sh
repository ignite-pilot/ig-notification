#!/bin/bash
# AWS용 Docker 이미지 빌드 및 푸시 스크립트

set -e

# 설정
AWS_REGION="ap-northeast-2"
ECR_REPOSITORY="ig-notification"
IMAGE_TAG="${1:-latest}"

# AWS 계정 ID 확인
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS credentials not configured"
    exit 1
fi

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "Building Docker image..."
docker build -f Dockerfile.aws -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

echo "Tagging image for ECR..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "Pushing image to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

echo "Successfully pushed ${ECR_URI}:${IMAGE_TAG}"

