import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
import pytest

import push_service
from push_service import PushService


class TestPushService:
    def setup_method(self):
        """각 테스트 전에 앱 캐시 초기화"""
        push_service._firebase_app_cache.clear()

    def _make_mock_app(self, project_id="test-project"):
        """Firebase 앱 mock 반환"""
        mockApp = MagicMock()
        mockApp.name = f"app_{project_id}"
        return mockApp

    # ── _get_firebase_app 관련 ───────────────────────────────────────────

    def test_get_firebase_app_no_package(self):
        """firebase-admin 미설치 시 RuntimeError"""
        with patch("push_service.FIREBASE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="firebase-admin 패키지"):
                PushService._get_firebase_app("test-project")

    def test_get_firebase_app_secret_not_found(self):
        """Secret이 없는 project_id → ValueError"""
        from botocore.exceptions import ClientError
        mockError = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'not found'}},
            'GetSecretValue'
        )
        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.boto3.client") as mockBotoClient:
            mockBotoClient.return_value.get_secret_value.side_effect = mockError
            with pytest.raises(ValueError, match="찾을 수 없습니다"):
                PushService._get_firebase_app("nonexistent-project")

    def test_get_firebase_app_not_service_account(self):
        """서비스 계정 형식이 아닌 Secret → ValueError"""
        import json
        mockSecret = json.dumps({"type": "other_type"})
        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.boto3.client") as mockBotoClient:
            mockBotoClient.return_value.get_secret_value.return_value = {
                'SecretString': mockSecret
            }
            with pytest.raises(ValueError, match="서비스 계정 키 형식"):
                PushService._get_firebase_app("bad-project")

    def test_get_firebase_app_cached(self):
        """캐시에 있으면 AWS 조회 없이 반환"""
        projectId = "cached-project"
        mockApp = self._make_mock_app(projectId)
        push_service._firebase_app_cache[projectId] = mockApp

        with patch("push_service.boto3.client") as mockBotoClient:
            result = PushService._get_firebase_app(projectId)

        assert result is mockApp
        mockBotoClient.assert_not_called()

    def test_get_firebase_app_initializes_and_caches(self):
        """초기화 성공 시 캐시에 저장"""
        import json
        projectId = "new-project"
        mockSecret = json.dumps({"type": "service_account", "project_id": projectId})
        mockApp = self._make_mock_app(projectId)

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.boto3.client") as mockBotoClient, \
             patch("push_service.credentials.Certificate"), \
             patch("push_service.firebase_admin.initialize_app", return_value=mockApp):
            mockBotoClient.return_value.get_secret_value.return_value = {
                'SecretString': mockSecret
            }
            result = PushService._get_firebase_app(projectId)

        assert result is mockApp
        assert push_service._firebase_app_cache[projectId] is mockApp

    # ── send_push 관련 ────────────────────────────────────────────────────

    def test_send_push_firebase_not_available(self):
        """firebase-admin 미설치 시 RuntimeError"""
        with patch("push_service.FIREBASE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="firebase-admin 패키지"):
                PushService.send_push(
                    firebase_project_id="test-project",
                    device_tokens=["token_abc"],
                    title="테스트",
                    body="내용"
                )

    def test_send_push_too_many_tokens(self):
        """501개 토큰 → ValueError"""
        tooManyTokens = [f"token_{i}" for i in range(501)]
        with pytest.raises(ValueError, match="500"):
            PushService.send_push(
                firebase_project_id="test-project",
                device_tokens=tooManyTokens,
                title="테스트",
                body="내용"
            )

    def test_send_push_success_single_token(self):
        """단일 토큰 발송 성공"""
        projectId = "test-project"
        mockApp = self._make_mock_app(projectId)
        push_service._firebase_app_cache[projectId] = mockApp

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.messaging") as mockMessaging:
            mockMessaging.Notification.return_value = MagicMock()
            mockMessaging.Message.return_value = MagicMock()
            mockMessaging.send.return_value = "projects/test/messages/abc"

            successCount, failureCount, failedTokens = PushService.send_push(
                firebase_project_id=projectId,
                device_tokens=["single_token_xyz"],
                title="단일 발송 테스트",
                body="테스트 내용"
            )

        assert successCount == 1
        assert failureCount == 0
        assert failedTokens == []
        mockMessaging.send.assert_called_once()

    def test_send_push_success_multiple_tokens(self):
        """다중 토큰 발송 성공"""
        projectId = "test-project"
        mockApp = self._make_mock_app(projectId)
        push_service._firebase_app_cache[projectId] = mockApp

        tokenList = ["token_a", "token_b", "token_c"]
        mockResponses = [MagicMock(success=True, exception=None) for _ in tokenList]
        mockBatchResponse = MagicMock(
            success_count=3, failure_count=0, responses=mockResponses
        )

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.messaging") as mockMessaging:
            mockMessaging.Notification.return_value = MagicMock()
            mockMessaging.Message.return_value = MagicMock()
            mockMessaging.send_each.return_value = mockBatchResponse

            successCount, failureCount, failedTokens = PushService.send_push(
                firebase_project_id=projectId,
                device_tokens=tokenList,
                title="다중 발송 테스트",
                body="테스트 내용",
                data={"key": "value"}
            )

        assert successCount == 3
        assert failureCount == 0
        assert failedTokens == []

    def test_send_push_partial_failure(self):
        """일부 토큰 실패 → 실패 토큰 목록 반환"""
        projectId = "test-project"
        mockApp = self._make_mock_app(projectId)
        push_service._firebase_app_cache[projectId] = mockApp

        tokenList = ["token_ok_1", "token_fail_1", "token_ok_2", "token_fail_2"]
        mockResponses = []
        for token in tokenList:
            mockResp = MagicMock()
            mockResp.success = "fail" not in token
            mockResp.exception = Exception(f"Invalid: {token}") if "fail" in token else None
            mockResponses.append(mockResp)

        mockBatchResponse = MagicMock(
            success_count=2, failure_count=2, responses=mockResponses
        )

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.messaging") as mockMessaging:
            mockMessaging.Notification.return_value = MagicMock()
            mockMessaging.Message.return_value = MagicMock()
            mockMessaging.send_each.return_value = mockBatchResponse

            successCount, failureCount, failedTokens = PushService.send_push(
                firebase_project_id=projectId,
                device_tokens=tokenList,
                title="부분 실패 테스트",
                body="테스트 내용"
            )

        assert successCount == 2
        assert failureCount == 2
        assert "token_fail_1" in failedTokens
        assert "token_fail_2" in failedTokens
        assert "token_ok_1" not in failedTokens

    def test_send_push_single_token_failure(self):
        """단일 토큰 발송 실패"""
        projectId = "test-project"
        mockApp = self._make_mock_app(projectId)
        push_service._firebase_app_cache[projectId] = mockApp
        failToken = "invalid_token_xyz"

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.messaging") as mockMessaging:
            mockMessaging.Notification.return_value = MagicMock()
            mockMessaging.Message.return_value = MagicMock()
            mockMessaging.send.side_effect = Exception("Token not registered")

            successCount, failureCount, failedTokens = PushService.send_push(
                firebase_project_id=projectId,
                device_tokens=[failToken],
                title="실패 테스트",
                body="내용"
            )

        assert successCount == 0
        assert failureCount == 1
        assert failToken in failedTokens

    def test_send_push_different_projects_use_different_apps(self):
        """서로 다른 project_id는 서로 다른 앱 인스턴스 사용"""
        projectA = "project-a"
        projectB = "project-b"
        mockAppA = self._make_mock_app(projectA)
        mockAppB = self._make_mock_app(projectB)
        push_service._firebase_app_cache[projectA] = mockAppA
        push_service._firebase_app_cache[projectB] = mockAppB

        calledApps = []

        with patch("push_service.FIREBASE_AVAILABLE", True), \
             patch("push_service.messaging") as mockMessaging:
            mockMessaging.Notification.return_value = MagicMock()
            mockMessaging.Message.return_value = MagicMock()

            def captureApp(*args, **kwargs):
                calledApps.append(kwargs.get('app'))
                return "msg_id"

            mockMessaging.send.side_effect = captureApp

            PushService.send_push(
                firebase_project_id=projectA,
                device_tokens=["token_1"],
                title="A 앱 테스트",
                body="내용"
            )
            PushService.send_push(
                firebase_project_id=projectB,
                device_tokens=["token_2"],
                title="B 앱 테스트",
                body="내용"
            )

        assert calledApps[0] is mockAppA
        assert calledApps[1] is mockAppB
        assert calledApps[0] is not calledApps[1]
