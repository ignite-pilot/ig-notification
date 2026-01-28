# Dockerfile for IG Notification System
# AWS ECS 배포용 Multi-stage build

# Stage 1: Frontend build
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies (빌드에 devDependencies 필요)
RUN npm ci

# Copy frontend source files
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code (config 디렉토리 포함)
COPY backend/ ./backend/

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PHASE=alpha \
    AWS_DEFAULT_REGION=ap-northeast-2

# Expose HTTP port
EXPOSE 8101

# Health check for ECS/ALB
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://127.0.0.1:8101/api/health || exit 1

# Run as non-root user for security
# Port 8101 doesn't require root, so we can use non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run the application
WORKDIR /app/backend
# uvicorn을 직접 실행 (포트 8101 고정)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8101"]
