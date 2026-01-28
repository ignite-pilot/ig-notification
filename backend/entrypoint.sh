#!/bin/bash
# ECS 배포용 entrypoint 스크립트
# 환경 변수에서 포트를 읽어서 uvicorn 실행

set -e

# 환경 변수에서 포트 읽기 (기본값: 8101)
PORT=${API_PORT:-8101}

# uvicorn 실행
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
