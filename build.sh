#!/bin/bash
# 통합 서버 빌드 스크립트
# Frontend를 빌드하고 Backend에서 서빙할 수 있도록 준비

set -e

echo "Building IG Notification System..."

# Frontend 빌드
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Backend 의존성 확인
echo "Checking backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "Build completed successfully!"
echo "Frontend build output: frontend/dist"
echo "To run the server: cd backend && source venv/bin/activate && python main.py"

