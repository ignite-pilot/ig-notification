import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import io
from typing import List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailService:
    MAX_ATTACHMENTS = 10
    MAX_TOTAL_SIZE = 30 * 1024 * 1024  # 30MB in bytes
    
    @staticmethod
    def validate_attachments(attachments: Optional[List[dict]]) -> Tuple[bool, str, int]:
        """
        Validate attachments
        Returns: (is_valid, error_message, total_size)
        """
        if not attachments:
            return True, "", 0
        
        if len(attachments) > EmailService.MAX_ATTACHMENTS:
            return False, f"첨부파일은 최대 {EmailService.MAX_ATTACHMENTS}개까지 가능합니다.", 0
        
        total_size = 0
        for att in attachments:
            if 'content' in att and 'filename' in att:
                try:
                    # Base64 decode to get actual size
                    content = base64.b64decode(att['content'])
                    total_size += len(content)
                except Exception as e:
                    return False, f"첨부파일 처리 중 오류: {str(e)}", 0
        
        if total_size > EmailService.MAX_TOTAL_SIZE:
            return False, f"첨부파일 총 크기는 {EmailService.MAX_TOTAL_SIZE / (1024*1024)}MB를 넘을 수 없습니다.", 0
        
        return True, "", total_size
    
    @staticmethod
    async def send_email(
        recipient_emails: List[str],
        sender_email: str,
        smtp_host: str,
        smtp_port: int,
        smtp_username: Optional[str],
        smtp_password: Optional[str],
        use_ssl: bool,
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send email using SMTP
        Returns: (success, error_message)
        """
        try:
            # Validate attachments
            is_valid, error_msg, total_size = EmailService.validate_attachments(attachments)
            if not is_valid:
                return False, error_msg
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            msg.attach(MIMEText(body, 'html' if '<html' in body.lower() else 'plain', 'utf-8'))
            
            # Add attachments
            if attachments:
                for att in attachments:
                    try:
                        content = base64.b64decode(att['content'])
                        filename = att['filename']
                        
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(content)
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        logger.error(f"첨부파일 추가 실패: {str(e)}")
                        return False, f"첨부파일 처리 중 오류: {str(e)}"
            
            # Prepare recipient list
            all_recipients = recipient_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Send email
            if use_ssl:
                await aiosmtplib.send(
                    msg,
                    hostname=smtp_host,
                    port=smtp_port,
                    username=smtp_username,
                    password=smtp_password,
                    use_tls=True,
                    start_tls=False
                )
            else:
                await aiosmtplib.send(
                    msg,
                    hostname=smtp_host,
                    port=smtp_port,
                    username=smtp_username,
                    password=smtp_password,
                    use_tls=False,
                    start_tls=True
                )
            
            return True, None
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {str(e)}")
            return False, str(e)

