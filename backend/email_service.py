import aiosmtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import io
import ssl
import certifi
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
        attachments: Optional[List[dict]] = None,
        verify_ssl: bool = True
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
            
            # Use MIMEMultipart (MIME format) with proper RFC 2231 encoding for filenames
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            msg.attach(MIMEText(body, 'html' if '<html' in body.lower() else 'plain', 'utf-8'))
            
            # Add attachments with proper RFC 2231 encoding and ASCII fallback
            if attachments:
                for att in attachments:
                    try:
                        content = base64.b64decode(att['content'])
                        filename = att['filename']
                        
                        # Create MIME part for attachment
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(content)
                        encoders.encode_base64(part)
                        
                        # Use tuple format for filename parameter to enable RFC 2231 encoding
                        # Format: filename=('utf-8', '', filename)
                        # This automatically generates: filename*=utf-8''encoded_value
                        # The email library handles the encoding internally
                        # This is the recommended approach per RFC 2231 standard
                        # 
                        # For maximum compatibility, we also add an ASCII fallback
                        # Some email clients (especially older ones) may not support filename*
                        import urllib.parse
                        try:
                            # Check if filename contains non-ASCII characters
                            filename.encode('ascii')
                            # ASCII only, use simple format
                            part.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=filename
                            )
                            part.set_param('name', filename, header='Content-Type')
                        except UnicodeEncodeError:
                            # Contains non-ASCII, use tuple format for RFC 2231
                            # This generates filename*=utf-8''encoded automatically
                            part.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=('utf-8', '', filename)
                            )
                            
                            # Also set Content-Type name parameter with same tuple format
                            part.set_param('name', ('utf-8', '', filename), header='Content-Type')
                        
                        msg.attach(part)
                        
                        # Log attachment header for debugging
                        logger.debug(f"첨부파일 헤더 - Content-Disposition: {part.get('Content-Disposition')}")
                        logger.debug(f"첨부파일 헤더 - Content-Type: {part.get('Content-Type')}")
                    except Exception as e:
                        logger.error(f"첨부파일 추가 실패: {str(e)}")
                        return False, f"첨부파일 처리 중 오류: {str(e)}"
            
            # Log full message structure for debugging
            logger.debug(f"이메일 메시지 타입: {type(msg).__name__}")
            logger.debug(f"첨부파일 수: {len(attachments) if attachments else 0}")
            
            # Prepare recipient list
            all_recipients = recipient_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Configure SSL/TLS settings
            # aiosmtplib supports validate_certs and cert_bundle parameters
            cert_bundle = None
            validate_certs = verify_ssl
            ssl_context = None
            
            if verify_ssl:
                # Use certifi's certificate bundle for proper validation
                try:
                    cert_bundle = certifi.where()
                    # Create SSL context with certifi for better compatibility
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    logger.debug(f"Using certifi bundle: {cert_bundle}")
                except Exception as e:
                    logger.warning(f"certifi 사용 실패: {str(e)}")
                    # Fallback: create SSL context manually
                    try:
                        ssl_context = ssl.create_default_context()
                    except Exception:
                        ssl_context = None
            else:
                # For self-signed certificates, disable validation
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                logger.debug("SSL verification disabled for self-signed certificates")
            
            # Send email using SMTP object
            # Port 465 uses implicit TLS (SMTP_SSL equivalent)
            # Port 587 uses STARTTLS
            smtp_kwargs = {
                'hostname': smtp_host,
                'port': smtp_port,
                'validate_certs': validate_certs,
            }
            
            # Always add cert_bundle if verify_ssl is True
            if verify_ssl and cert_bundle:
                smtp_kwargs['cert_bundle'] = cert_bundle
            
            # Always add tls_context (both for verify_ssl True and False)
            if ssl_context:
                smtp_kwargs['tls_context'] = ssl_context
            
            if use_ssl:
                # Port 465: 암묵적 TLS (SMTP_SSL 방식)
                smtp_kwargs['use_tls'] = True
                smtp_kwargs['start_tls'] = False
            else:
                # Port 587: STARTTLS 방식
                smtp_kwargs['use_tls'] = False
                smtp_kwargs['start_tls'] = True
            
            smtp = aiosmtplib.SMTP(**smtp_kwargs)
            
            await smtp.connect()
            if smtp_username and smtp_password:
                await smtp.login(smtp_username, smtp_password)
            
            # Log message structure before sending (for debugging)
            logger.debug("=== 이메일 메시지 구조 (전송 전) ===")
            msg_str = msg.as_string()
            for line in msg_str.split('\n'):
                if 'Content-Disposition' in line or 'Content-Type' in line or 'filename' in line.lower() or 'name*' in line.lower():
                    logger.debug(f"  {line}")
            
            await smtp.send_message(msg)
            await smtp.quit()
            
            return True, None
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {str(e)}")
            return False, str(e)

