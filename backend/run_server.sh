#!/bin/bash
# 서버 실행 스크립트

cd "$(dirname "$0")"

# 가상환경 활성화
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 의존성 설치 확인
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# 환경 변수 설정
export PHASE=${PHASE:-local}

# 서버 실행
echo "Starting server on port 8101..."
echo "Access the server at: http://localhost:8101"
python main.py

