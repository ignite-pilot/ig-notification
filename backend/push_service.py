import logging
import json
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# firebase_admin은 선택적 의존성
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin 패키지가 설치되지 않았습니다. 푸시 알림 기능이 비활성화됩니다.")

# 앱별 Firebase 앱 인스턴스 캐시 {firebase_project_id: firebase_admin.App}
_firebase_app_cache = {}


def _load_service_account_from_aws(firebase_project_id: str) -> dict:
    """
    AWS Secrets Manager에서 Firebase 서비스 계정 JSON 로드.
    Secret 이름 규칙: prod/ignite-pilot/{firebase_project_id}-android-key
    """
    secret_id = f"prod/ignite-pilot/{firebase_project_id}-android-key"
    try:
        client = boto3.client('secretsmanager', region_name='ap-northeast-2')
        response = client.get_secret_value(SecretId=secret_id)
        secret = json.loads(response['SecretString'])
        if secret.get('type') != 'service_account':
            raise ValueError(f"Secret '{secret_id}'이 서비스 계정 키 형식이 아닙니다.")
        return secret
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            raise ValueError(f"Secret '{secret_id}'을 찾을 수 없습니다. AWS Secrets Manager에 등록되어 있는지 확인하세요.")
        raise RuntimeError(f"AWS Secrets Manager 조회 실패: {str(e)}")
    except json.JSONDecodeError:
        raise ValueError(f"Secret '{secret_id}'의 내용이 유효한 JSON이 아닙니다.")


class PushService:
    MAX_TOKENS = 500

    @classmethod
    def _get_firebase_app(cls, firebase_project_id: str) -> 'firebase_admin.App':
        """
        firebase_project_id에 해당하는 Firebase 앱 인스턴스 반환.
        캐시에 없으면 AWS Secrets Manager에서 서비스 계정 키를 로드해 초기화.
        """
        if not FIREBASE_AVAILABLE:
            raise RuntimeError("firebase-admin 패키지가 설치되지 않았습니다.")

        if firebase_project_id in _firebase_app_cache:
            return _firebase_app_cache[firebase_project_id]

        logger.info(f"Firebase 앱 초기화 중: project_id={firebase_project_id}")
        service_account_info = _load_service_account_from_aws(firebase_project_id)
        cred = credentials.Certificate(service_account_info)

        # firebase_admin은 앱 이름으로 구분 (DEFAULT는 첫 번째 앱에만 사용)
        app_name = f"app_{firebase_project_id}"
        try:
            app = firebase_admin.initialize_app(cred, name=app_name)
        except ValueError:
            # 이미 동일 이름으로 초기화된 경우 (동시 요청 레이스 컨디션 방어)
            app = firebase_admin.get_app(app_name)

        _firebase_app_cache[firebase_project_id] = app
        logger.info(f"Firebase 앱 초기화 완료: project_id={firebase_project_id}")
        return app

    @classmethod
    def send_push(
        cls,
        firebase_project_id: str,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> Tuple[int, int, List[str]]:
        """
        FCM 푸시 알림 발송.

        Args:
            firebase_project_id: Firebase 프로젝트 ID (Secret 조회에 사용)
            device_tokens: 디바이스 토큰 목록 (최대 500개)
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (선택, 모든 값은 문자열로 변환)

        Returns:
            Tuple[success_count, failure_count, failed_tokens]
        """
        if len(device_tokens) > cls.MAX_TOKENS:
            raise ValueError(f"토큰은 최대 {cls.MAX_TOKENS}개까지 허용됩니다.")

        app = cls._get_firebase_app(firebase_project_id)

        # FCM data 값은 모두 문자열이어야 함
        str_data = {k: str(v) for k, v in data.items()} if data else None
        notification = messaging.Notification(title=title, body=body)

        if len(device_tokens) == 1:
            message = messaging.Message(
                notification=notification,
                data=str_data,
                token=device_tokens[0]
            )
            try:
                messaging.send(message, app=app)
                return 1, 0, []
            except Exception as e:
                logger.error(f"단일 토큰 발송 실패 ({device_tokens[0]}): {str(e)}")
                return 0, 1, [device_tokens[0]]
        else:
            messages = [
                messaging.Message(
                    notification=notification,
                    data=str_data,
                    token=token
                )
                for token in device_tokens
            ]
            try:
                batch_response = messaging.send_each(messages, app=app)
            except Exception as e:
                logger.error(f"다중 토큰 발송 실패: {str(e)}")
                return 0, len(device_tokens), list(device_tokens)

            failedTokens = []
            for idx, resp in enumerate(batch_response.responses):
                if not resp.success:
                    failedTokens.append(device_tokens[idx])
                    logger.warning(f"토큰 발송 실패 ({device_tokens[idx]}): {resp.exception}")

            return batch_response.success_count, batch_response.failure_count, failedTokens
