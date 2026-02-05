"""
Email Service Route - Gmail SMTP Integration
Add this to your routes.py file
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import aiosmtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

email_router = APIRouter(prefix="/email", tags=["email"])


class SMTPConfig(BaseModel):
    host: str = "smtp.gmail.com"
    port: int = 587
    user: str
    pass_: str


class EmailRequest(BaseModel):
    to: EmailStr
    from_: EmailStr = Field(alias="from")
    subject: str
    html: str
    smtpConfig: SMTPConfig


@email_router.post("/send")
async def send_email(request: EmailRequest):
    """
    Send email via Gmail SMTP
    
    Requires Gmail App Password:
    1. Enable 2-Step Verification in Google Account
    2. Go to Security → App passwords
    3. Generate password for "Mail" app
    4. Use the 16-character password here
    """
    
    try:
        # Create email message
        message = EmailMessage()
        message["From"] = request.from_
        message["To"] = request.to
        message["Subject"] = request.subject
        message.set_content("Please view this email in HTML mode")
        message.add_alternative(request.html, subtype="html")
        
        # Send via Gmail SMTP
        await aiosmtplib.send(
            message,
            hostname=request.smtpConfig.host,
            port=request.smtpConfig.port,
            username=request.smtpConfig.user,
            password=request.smtpConfig.pass_,
            start_tls=True,
            timeout=30
        )
        
        logger.info(f"Email sent successfully to {request.to}")
        
        return {
            "success": True,
            "message": "Email sent successfully",
            "to": request.to
        }
        
    except aiosmtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="SMTP authentication failed. Check your Gmail App Password."
        )
        
    except aiosmtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@email_router.post("/test")
async def test_email_config(smtp_config: SMTPConfig):
    """Test SMTP configuration"""
    
    try:
        # Simple SMTP connection test
        async with aiosmtplib.SMTP(
            hostname=smtp_config.host,
            port=smtp_config.port,
            timeout=10
        ) as smtp:
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(smtp_config.user, smtp_config.pass_)
            
        return {
            "success": True,
            "message": "SMTP configuration is valid"
        }
        
    except aiosmtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Authentication failed. Check your Gmail App Password."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Configuration test failed: {str(e)}"
        }
