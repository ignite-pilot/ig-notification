내 프로젝트를 AWS용 Docker 이미지로 만들고 싶어. 현재 로컬은 Docker 없이 실행되고 있어.

요구사항:
- 외부 서비스 도메인 : ig-notification.ignite-pilot.com
- 컨테이너는 HTTP 서버로 동작해야 함.
- AWS에서 기존에 만들어둔 ALB 뒤에서 서비스됨(HTTPS 처리는 ALB에서 할 예정, 컨테이너는 HTTP만).
- DB 정보 및 주요 설정값은 AWS Secrets Manager에서 가져오고 있고, AWS용 Docker에서도 동일하게 Secrets Manager 기반으로 동작해야 함.
- Docker 이미지 내부에 Access Key/Secret Key를 하드코딩하지 말고,  ECS Task Definition의 secrets로 환경변수 주입하는 방식으로 해줘
- 로그는 stdout/stderr로 출력되도록(CloudWatch 수집 가정).
