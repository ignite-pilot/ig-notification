"""
MCP Server for IG Notification System
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from email_service import EmailService
from database import SessionLocal, EmailLog
from datetime import datetime
import uuid


class MCPServer:
    def __init__(self):
        self.email_service = EmailService()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP protocol requests
        """
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "send_email":
            return await self.send_email(params)
        elif method == "get_email_log":
            return await self.get_email_log(params)
        elif method == "list_email_logs":
            return await self.list_email_logs(params)
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email via MCP
        """
        try:
            # Extract parameters
            recipient_emails = params.get("recipient_emails", [])
            sender_email = params.get("sender_email")
            smtp_host = params.get("smtp_host")
            smtp_port = params.get("smtp_port")
            smtp_username = params.get("smtp_username")
            smtp_password = params.get("smtp_password")
            use_ssl = params.get("use_ssl", True)
            cc_emails = params.get("cc_emails")
            bcc_emails = params.get("bcc_emails")
            subject = params.get("subject")
            body = params.get("body")
            attachments = params.get("attachments")  # List of {filename, content_base64}
            
            # Validate
            if not recipient_emails or len(recipient_emails) == 0:
                return {
                    "error": {
                        "code": -32602,
                        "message": "받는 사람 이메일을 최소 1개 이상 입력해주세요."
                    }
                }
            
            if len(recipient_emails) > 100:
                return {
                    "error": {
                        "code": -32602,
                        "message": "최대 100명까지 발송 가능합니다."
                    }
                }
            
            # Create email log
            db = SessionLocal()
            try:
                email_log = EmailLog(
                    sender_email=sender_email,
                    recipient_emails=recipient_emails,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                    subject=subject,
                    body=body,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    use_ssl="true" if use_ssl else "false",
                    status="pending",
                    attachment_count=len(attachments) if attachments else 0,
                    total_attachment_size=0  # Will be calculated in email_service
                )
                db.add(email_log)
                db.commit()
                db.refresh(email_log)
                
                # Convert attachments format if needed
                att_list = None
                if attachments:
                    att_list = []
                    for att in attachments:
                        att_list.append({
                            'filename': att.get('filename'),
                            'content': att.get('content_base64')
                        })
                
                # Send email
                success, error_message = await EmailService.send_email(
                    recipient_emails=recipient_emails,
                    sender_email=sender_email,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    use_ssl=use_ssl,
                    subject=subject,
                    body=body,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                    attachments=att_list
                )
                
                # Update log
                if success:
                    email_log.status = "success"
                    email_log.sent_at = datetime.utcnow()
                else:
                    email_log.status = "failed"
                    email_log.error_message = error_message
                
                db.commit()
                
                return {
                    "result": {
                        "log_id": str(email_log.id),
                        "status": email_log.status,
                        "message": "이메일이 성공적으로 발송되었습니다." if success else f"이메일 발송 실패: {error_message}",
                        "created_at": email_log.created_at.isoformat()
                    }
                }
            finally:
                db.close()
                
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def get_email_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get email log by ID
        """
        try:
            log_id = params.get("log_id")
            if not log_id:
                return {
                    "error": {
                        "code": -32602,
                        "message": "log_id is required"
                    }
                }
            
            db = SessionLocal()
            try:
                log = db.query(EmailLog).filter(EmailLog.id == uuid.UUID(log_id)).first()
                if not log:
                    return {
                        "error": {
                            "code": -32602,
                            "message": "로그를 찾을 수 없습니다."
                        }
                    }
                
                return {
                    "result": {
                        "id": str(log.id),
                        "sender_email": log.sender_email,
                        "recipient_emails": log.recipient_emails,
                        "cc_emails": log.cc_emails,
                        "bcc_emails": log.bcc_emails,
                        "subject": log.subject,
                        "body": log.body,
                        "smtp_host": log.smtp_host,
                        "smtp_port": log.smtp_port,
                        "use_ssl": log.use_ssl,
                        "status": log.status,
                        "error_message": log.error_message,
                        "attachment_count": log.attachment_count,
                        "total_attachment_size": log.total_attachment_size,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                        "sent_at": log.sent_at.isoformat() if log.sent_at else None
                    }
                }
            finally:
                db.close()
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def list_email_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List email logs
        """
        try:
            skip = params.get("skip", 0)
            limit = params.get("limit", 100)
            
            db = SessionLocal()
            try:
                logs = db.query(EmailLog).order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
                
                result = []
                for log in logs:
                    result.append({
                        "id": str(log.id),
                        "sender_email": log.sender_email,
                        "recipient_emails": log.recipient_emails,
                        "subject": log.subject,
                        "status": log.status,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                        "sent_at": log.sent_at.isoformat() if log.sent_at else None
                    })
                
                return {
                    "result": {
                        "logs": result,
                        "total": len(result)
                    }
                }
            finally:
                db.close()
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


async def main():
    """
    MCP Server main loop
    """
    server = MCPServer()
    
    # Simple HTTP server for MCP protocol
    from aiohttp import web
    import aiohttp_cors
    
    async def handle_mcp_request(request):
        try:
            data = await request.json()
            response = await server.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            return web.json_response({
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }, status=400)
    
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    app.router.add_post("/mcp", handle_mcp_request)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    from config import settings
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.mcp_port)
    await site.start()
    
    print(f"MCP Server running on port {settings.mcp_port}")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

