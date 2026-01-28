# EC2 인스턴스 비용 정보

## 현재 인스턴스
- **Instance ID**: `i-08eb9d8a486cf0692`
- **Instance Type**: `t3.small`
- **Region**: `ap-northeast-2` (서울)

## 예상 비용

### t3.small 인스턴스 비용 (ap-northeast-2)
- **On-Demand**: 약 $0.0208/시간 (약 ₩28/시간)
- **1시간 사용**: 약 ₩28
- **10분 사용**: 약 ₩5

### 비용 절감 방법

1. **빌드 완료 후 즉시 종료** (권장)
   ```bash
   aws ec2 terminate-instances \
     --instance-ids i-08eb9d8a486cf0692 \
     --region ap-northeast-2
   ```

2. **빌드 중에도 모니터링**
   - 빌드가 완료되면 즉시 종료
   - 예상 소요 시간: 10-15분
   - 예상 비용: 약 ₩5-7

## 빌드 완료 확인

빌드가 완료되었는지 확인:
```bash
# ECR에 새 이미지가 푸시되었는지 확인
aws ecr describe-images \
  --repository-name ig-notification \
  --region ap-northeast-2 \
  --query 'imageDetails[0].imagePushedAt'
```

## 인스턴스 종료 명령어

빌드가 완료되면:
```bash
aws ec2 terminate-instances \
  --instance-ids i-08eb9d8a486cf0692 \
  --region ap-northeast-2
```

또는 AWS 콘솔에서:
1. EC2 → Instances
2. 인스턴스 선택 → "Instance state" → "Terminate instance"

## 참고

- **Stop vs Terminate**: 
  - Stop: 인스턴스를 중지 (스토리지 비용 계속 발생)
  - Terminate: 인스턴스 완전 삭제 (비용 없음) ✅ 권장

- **빌드 완료 후 반드시 종료하세요!**

