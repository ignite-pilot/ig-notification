#!/bin/bash
# EC2 인스턴스에서 원격으로 빌드하는 스크립트
# AWS Systems Manager Session Manager 또는 EC2 Instance Connect 사용

set -e

INSTANCE_ID="i-08eb9d8a486cf0692"
AWS_REGION="ap-northeast-2"
ECR_URI="575084400422.dkr.ecr.ap-northeast-2.amazonaws.com/ig-notification"
IMAGE_TAG="${1:-latest}"

echo "=========================================="
echo "EC2에서 원격 빌드 실행"
echo "=========================================="
echo ""

# AWS Systems Manager Session Manager를 사용하여 명령 실행
echo "EC2 인스턴스에서 빌드 명령 실행 중..."

aws ssm send-command \
  --instance-ids ${INSTANCE_ID} \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[
    'cd ~',
    'if [ ! -d ig-notification ]; then git clone https://github.com/ignite-pilot/ig-notification.git; fi',
    'cd ig-notification',
    'git pull || true',
    'docker build -f Dockerfile.aws -t ig-notification:${IMAGE_TAG} .',
    'aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}',
    'docker tag ig-notification:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}',
    'docker push ${ECR_URI}:${IMAGE_TAG}',
    'echo \"✅ 빌드 및 푸시 완료!\"'
  ]" \
  --region ${AWS_REGION} \
  --output text \
  --query 'Command.CommandId' > /tmp/command-id.txt

COMMAND_ID=$(cat /tmp/command-id.txt)
echo "Command ID: ${COMMAND_ID}"
echo ""
echo "빌드 진행 상황 확인:"
echo "  aws ssm get-command-invocation --command-id ${COMMAND_ID} --instance-id ${INSTANCE_ID} --region ${AWS_REGION}"
echo ""

# 빌드 완료 대기
echo "빌드 완료 대기 중 (약 5-10분 소요)..."
sleep 30

for i in {1..20}; do
  STATUS=$(aws ssm get-command-invocation \
    --command-id ${COMMAND_ID} \
    --instance-id ${INSTANCE_ID} \
    --region ${AWS_REGION} \
    --query 'Status' \
    --output text 2>/dev/null || echo "InProgress")
  
  if [ "$STATUS" = "Success" ]; then
    echo "✅ 빌드 완료!"
    aws ssm get-command-invocation \
      --command-id ${COMMAND_ID} \
      --instance-id ${INSTANCE_ID} \
      --region ${AWS_REGION} \
      --query 'StandardOutputContent' \
      --output text
    break
  elif [ "$STATUS" = "Failed" ]; then
    echo "❌ 빌드 실패"
    aws ssm get-command-invocation \
      --command-id ${COMMAND_ID} \
      --instance-id ${INSTANCE_ID} \
      --region ${AWS_REGION} \
      --query 'StandardErrorContent' \
      --output text
    exit 1
  else
    echo "진행 중... ($i/20)"
    sleep 30
  fi
done

echo ""
echo "=========================================="
echo "빌드 완료!"
echo "=========================================="

