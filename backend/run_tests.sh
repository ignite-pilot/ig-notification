#!/bin/bash

# Backend 테스트 실행 스크립트

echo "Backend 테스트를 시작합니다..."

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 테스트 실행
pytest tests/ -v

echo "테스트 완료"

