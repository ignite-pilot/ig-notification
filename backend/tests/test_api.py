from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)


class TestEmailAPI:
    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_send_email_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        response = client.post("/api/v1/email/send", data={})
        assert response.status_code == 422  # Validation error

    def test_send_email_invalid_recipient_count(self):
        """받는 사람 수 초과 테스트"""
        recipient_emails = [f"test{i}@example.com" for i in range(101)]
        data = {
            "recipient_emails": json.dumps(recipient_emails),
            "sender_email": "sender@example.com",
            "smtp_host": "smtp.example.com",
            "smtp_port": "587",
            "subject": "Test",
            "body": "Test body"
        }
        response = client.post("/api/v1/email/send", data=data)
        assert response.status_code == 400
        assert "100명까지" in response.json()["detail"]

    def test_send_email_empty_recipients(self):
        """받는 사람이 없는 경우 테스트"""
        data = {
            "recipient_emails": json.dumps([]),
            "sender_email": "sender@example.com",
            "smtp_host": "smtp.example.com",
            "smtp_port": "587",
            "subject": "Test",
            "body": "Test body"
        }
        response = client.post("/api/v1/email/send", data=data)
        assert response.status_code == 400
        assert "최소 1개 이상" in response.json()["detail"]

    def test_get_email_logs(self):
        """로그 조회 테스트"""
        response = client.get("/api/v1/email/logs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_email_log_not_found(self):
        """존재하지 않는 로그 조회 테스트"""
        import uuid
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/email/logs/{fake_id}")
        assert response.status_code == 404

