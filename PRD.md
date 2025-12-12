
# 공통 Notification 모듈 
- 공통 Notification프로젝트는 알림을 발송해주는 공통 모듈입니다.
- 모든 작업은 Sequential Thinking을 사용해서 수행해 주세요.
- 디자인 컨셉은 Simple한 디자인으로 해 주세요.
- 회원 관리 프로젝트는 API로 작동을 합니다만, 메일 발송할 수 있는 UI도 이쁘게 만들어 주세요.
- 공통 Notification 프로젝트는 아래 기능을 가집니다.
	- Email 발송
		- 외부에서 인입된 이메일 발송 정보를 받아서 이메일을 발송합니다.
		- 발송할 smtp 주소도 입력으로 받습니다.
		- 첨부파일은 10개까지 가능하고, 총합은 30MB를 넘을수 없습니다.
		- 한번에 최대 100명까지 발송이 가능합니다.
- 공통 Notification 시스템은 별도의 Database를 가져서 발송 로그를 기록합니다.
- 테스트를 위한 UI에는 다음 항목을 입력 받습니다.
	- Email 발송
		- 받는 사람 이메일 N개
		- 보내는 사람 이메일
		- SMTP 주소,포트등 필요 정보. SSL 연동
		- 참조자 이메일 N개
		- 숨은 참조 이메일 N개
		- 메일 제목
		- 메일 본문
		- 첨부 파일



# MCP 서버
- 공통 Notification 시스템은 MCP(Model Context Protocol) 서버로 외부 서비스에 제공됩니다. 
- 외부 서비스들은 공통 Notification 시스템을 API 호출로만 사용합니다.

# 실행 Guide
    - DB 생성 및 Git Repository 생성은 아래 설정 Guide를 참고해서 생성해줘
	- 개발코드는 보안에 문제가 되지 않도록 개발을 해줘
    - 개발이 모두 완료 된 후에, 이 사이트의 모든 기능에 대해서 테스트 항목을 Sequential Thinking을 사용해서 만들어 주고, 실제 BE 및 FE unit test도 진행해주고, fail이 난 부분에 대해서는 바로 수정도 해 주세요.
	- 또한, 보안적으로 문제가 없는지 체크해 주고 문제가 있으면 수정해줘
	- 모든 코드 수정이 이뤄진 후에는 매번 unit test와 보안 체크를 수행하고 버그가 있으면 바로 수정해줘
	- 개발 언어
	- Backend : Python
	- Frontend : 괜찮은 걸로 알아서 진행

# 설정 Guide
- Github 
	- id : yunsik.cho@ignite.co.kr
	- github에 ig-notification라는 프로젝트를 private로 생성해줘
	- Personal Access Key : AWS Secret Manager "prod/ignite-pilot/github"에서 참고
- Database 
	- Local
		- 사용 DB : postgres
		- DB 정보 : AWS Secret Manager "prod/ignite-pilot/postgresInfo2"에서 참고
		- DB name : ig-notification
	- Alpha
		- 사용 DB : postgres
		- DB 정보 : AWS Secret Manager "prod/ignite-pilot/postgresInfo2"에서 참고
		- DB name : ig-notification-alpha

- 서비스 URL
	- Local
		- Frontend : http://localhost:8100
		- Backend : http://localhost:8101
		- MCP Server : http://localhost:8102
	- Alpha
		- Frontend : http://alpha.ig-notification.ig-pilot.com:8100
		- Backend : http://alpha.ig-notification.ig-pilot.com:8101
		- MCP Server : http://alpha.ig-notification.ig-pilot.com:8102



# 설치 및 실행 방법

## Backend 설정

1. Backend 디렉토리로 이동:
```bash
cd backend
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일을 열어서 데이터베이스 URL을 확인하세요
```

5. 데이터베이스 초기화:
```bash
python -c "from database import init_db; init_db()"
```

6. API 서버 실행:
```bash
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000
```

7. MCP 서버 실행 (별도 터미널):
```bash
python mcp_server.py
```

## Frontend 설정

1. Frontend 디렉토리로 이동:
```bash
cd frontend
```

2. 의존성 설치:
```bash
npm install
```

3. 개발 서버 실행:
```bash
npm run dev
```

Frontend는 http://localhost:3000 에서 실행됩니다.

## API 엔드포인트

### REST API (포트 8101)

**정확한 엔드포인트**:
- `POST /api/v1/email/send` - 이메일 발송 (multipart/form-data)
- `GET /api/v1/email/logs` - 발송 로그 조회
- `GET /api/v1/email/logs/{log_id}` - 특정 로그 상세 조회
- `GET /health` - 헬스 체크

**API 문서**:
- **상세 API 문서**: `API_DOCUMENTATION.md` 참고
- **Swagger UI**: http://localhost:8101/docs
- **ReDoc**: http://localhost:8101/redoc
- **OpenAPI JSON**: http://localhost:8101/openapi.json

**요청 형식**: `multipart/form-data` (이메일 발송 API)

**서버 URL**: `http://localhost:8101`

## MCP 서버 엔드포인트

- `POST /mcp` - MCP 프로토콜 요청 처리
  - `send_email` - 이메일 발송
  - `get_email_log` - 로그 조회
  - `list_email_logs` - 로그 목록 조회

## MCP 클라이언트 설정

외부 서비스에서 IG Notification MCP 서버를 사용하려면 다음 파일을 참고하세요:

- **설정 파일 예제**: `mcp-client-config.example.json`
- **사용 가이드**: `MCP_CLIENT_GUIDE.md`

MCP 서버는 `http://localhost:8102/mcp`에서 실행되며, HTTP POST 요청을 통해 JSON-RPC 스타일의 메서드를 호출할 수 있습니다.
