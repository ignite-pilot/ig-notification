import base64
from email_service import EmailService


class TestEmailService:
    def test_validate_attachments_no_attachments(self):
        """첨부파일이 없는 경우"""
        is_valid, error_msg, total_size = EmailService.validate_attachments(None)
        assert is_valid is True
        assert error_msg == ""
        assert total_size == 0

    def test_validate_attachments_max_count_exceeded(self):
        """첨부파일 개수 초과 테스트"""
        attachments = [{'filename': f'file{i}.txt', 'content': base64.b64encode(b'test').decode()} for i in range(11)]
        is_valid, error_msg, total_size = EmailService.validate_attachments(attachments)
        assert is_valid is False
        assert "10개까지" in error_msg

    def test_validate_attachments_max_size_exceeded(self):
        """첨부파일 총 크기 초과 테스트"""
        # 31MB 크기의 파일 생성
        large_content = b'x' * (31 * 1024 * 1024)
        attachments = [{
            'filename': 'large_file.txt',
            'content': base64.b64encode(large_content).decode()
        }]
        is_valid, error_msg, total_size = EmailService.validate_attachments(attachments)
        assert is_valid is False
        assert "30" in error_msg and "MB" in error_msg

    def test_validate_attachments_valid(self):
        """유효한 첨부파일 테스트"""
        attachments = [
            {'filename': 'file1.txt', 'content': base64.b64encode(b'test1').decode()},
            {'filename': 'file2.txt', 'content': base64.b64encode(b'test2').decode()}
        ]
        is_valid, error_msg, total_size = EmailService.validate_attachments(attachments)
        assert is_valid is True
        assert error_msg == ""
        assert total_size > 0

