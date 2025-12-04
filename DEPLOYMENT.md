# 배포 가이드

## Phase별 배포 설정

이 프로젝트는 Phase(환경)별로 다른 설정을 사용합니다.

### 지원하는 Phase

1. **local** - 로컬 개발 환경
2. **alpha** - Alpha 서버 환경 (AWS)

## Phase 설정 방법

### 환경 변수로 Phase 선택

```bash
# Local 환경
export PHASE=local

# Alpha 환경
export PHASE=alpha
```

또는 `.env` 파일에 설정:

```bash
PHASE=local  # 또는 alpha
```

## Phase별 설정

### Local 환경

- **Host**: `localhost`
- **API Port**: `8101` (기본값)
- **MCP Port**: `8102` (기본값)
- **Frontend Port**: `8100` (기본값)
- **CORS**: `http://localhost:8100`, `http://127.0.0.1:8100`
- **Log Level**: `DEBUG` (기본값)
- **API Key**: 선택사항

### Alpha 환경

- **Host**: `alpha.ig-notification.ig-pilot.com`
- **API Port**: `8101` (기본값)
- **MCP Port**: `8102` (기본값)
- **Frontend Port**: `8100` (기본값)
- **CORS**: `https://alpha.ig-notification.ig-pilot.com`
- **Log Level**: `INFO` (기본값)
- **API Key**: 필수 권장

## 실행 방법

### Local 환경에서 실행

```bash
# Backend
cd backend
export PHASE=local
source venv/bin/activate
python main.py  # localhost:8101

# MCP Server
python mcp_server.py  # localhost:8102

# Frontend
cd frontend
export PHASE=local
npm run dev  # localhost:8100
```

### Alpha 환경에서 실행

```bash
# Backend
cd backend
export PHASE=alpha
export API_KEY=your-secret-api-key  # 필수 권장
source venv/bin/activate
python main.py  # alpha.ig-notification.ig-pilot.com:8101

# MCP Server
python mcp_server.py  # alpha.ig-notification.ig-pilot.com:8102

# Frontend
cd frontend
export PHASE=alpha
npm run dev  # alpha.ig-notification.ig-pilot.com:8100
```

## 환경 변수 설정

### Local 환경 (.env)

```bash
PHASE=local
DATABASE_URL=postgresql://user:password@host:port/database_name
API_PORT=8101
MCP_PORT=8102
FRONTEND_PORT=8100
LOG_LEVEL=DEBUG
# API_KEY=  # 선택사항
```

### Alpha 환경 (.env)

```bash
PHASE=alpha
DATABASE_URL=postgresql://user:password@host:port/database_name
API_PORT=8101
MCP_PORT=8102
FRONTEND_PORT=8100
LOG_LEVEL=INFO
API_KEY=your-secret-api-key  # 필수 권장
```

## 포트 커스터마이징

각 Phase별로 포트를 환경 변수로 변경할 수 있습니다:

```bash
# Local 환경에서 포트 변경
export PHASE=local
export API_PORT=9001
export MCP_PORT=9002
export FRONTEND_PORT=9000

# Alpha 환경에서 포트 변경
export PHASE=alpha
export API_PORT=8101
export MCP_PORT=8102
export FRONTEND_PORT=8100
```

## 새로운 Phase 추가

새로운 Phase를 추가하려면:

1. `backend/config/` 디렉토리에 새 설정 파일 생성 (예: `production.py`)
2. `backend/config/__init__.py`에 Phase 추가
3. 필요한 경우 `frontend/vite.config.js`에 Phase별 설정 추가

예시:

```python
# backend/config/production.py
class ProductionConfig:
    HOST: str = "ig-notification.ig-pilot.com"
    API_PORT: int = 8101
    MCP_PORT: int = 8102
    FRONTEND_PORT: int = 8100
    ALLOWED_ORIGINS: list = [
        "https://ig-notification.ig-pilot.com"
    ]
    LOG_LEVEL: str = "INFO"
    ENV_NAME: str = "production"
```

## 주의사항

1. **Alpha 환경에서는 API_KEY 설정을 강력히 권장합니다**
2. **프로덕션 환경에서는 HTTPS를 사용하세요**
3. **CORS 설정은 보안상 필요한 도메인만 허용하세요**
4. **로그 레벨은 프로덕션에서 INFO 이상을 사용하세요**

