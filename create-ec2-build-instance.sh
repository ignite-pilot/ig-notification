#!/bin/bash
# EC2 인스턴스 생성 스크립트 (빌드용)

set -e

AWS_REGION="ap-northeast-2"
INSTANCE_TYPE="t3.small"  # x86_64 아키텍처 (Free Tier 제한 고려)
KEY_NAME="${1:-your-key-name}"  # 키 페어 이름을 인자로 받거나 수정 필요
SECURITY_GROUP_ID="${2:-sg-06ce21d40d4c0d090}"  # 기존 보안 그룹 사용

echo "=========================================="
echo "EC2 빌드 인스턴스 생성"
echo "=========================================="
echo ""

# AMI ID 조회 (Ubuntu 22.04 LTS x86_64)
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region ${AWS_REGION})

echo "사용할 AMI: ${AMI_ID}"

# 사용자 데이터 스크립트 (Docker 및 필요한 도구 설치)
USER_DATA=$(cat << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y docker.io git unzip curl
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# AWS CLI 설치
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# 프로젝트 클론
su - ubuntu -c "git clone https://github.com/ignite-pilot/ig-notification.git || true"
EOF
)

echo ""
echo "EC2 인스턴스 생성 중..."
echo "인스턴스 타입: ${INSTANCE_TYPE}"
echo "AMI: ${AMI_ID}"
echo ""

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id ${AMI_ID} \
  --instance-type ${INSTANCE_TYPE} \
  --key-name ${KEY_NAME} \
  --security-group-ids ${SECURITY_GROUP_ID} \
  --user-data "$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ig-notification-builder},{Key=Purpose,Value=build-docker-image}]" \
  --query 'Instances[0].InstanceId' \
  --output text \
  --region ${AWS_REGION})

echo "인스턴스 생성됨: ${INSTANCE_ID}"
echo ""

# Public IP 대기
echo "인스턴스 시작 대기 중..."
aws ec2 wait instance-running --instance-ids ${INSTANCE_ID} --region ${AWS_REGION}

sleep 10  # 사용자 데이터 스크립트 실행 대기

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids ${INSTANCE_ID} \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text \
  --region ${AWS_REGION})

echo ""
echo "=========================================="
echo "인스턴스 생성 완료!"
echo "=========================================="
echo "Instance ID: ${INSTANCE_ID}"
echo "Public IP: ${PUBLIC_IP}"
echo ""
echo "SSH 연결:"
echo "  ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo ""
echo "빌드 스크립트 실행:"
echo "  ./build-on-ec2.sh"
echo ""
echo "인스턴스 삭제 (빌드 완료 후):"
echo "  aws ec2 terminate-instances --instance-ids ${INSTANCE_ID} --region ${AWS_REGION}"

