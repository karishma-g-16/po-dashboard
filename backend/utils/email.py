import logging
import json
import http.client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

logger = logging.getLogger(__name__)

def send_reset_code_email(to_email: str, code: str):
    """
    Send a password reset verification code via email.
    Uses direct HTTP to SendGrid (No library needed) to bypass Render build issues.
    """
    # 1. Try SendGrid API via direct HTTP request (No dependency)
    if settings.SENDGRID_API_KEY:
        try:
            conn = http.client.HTTPSConnection("api.sendgrid.com")
            payload = json.dumps({
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": "Your Password Reset Verification Code"
                }],
                "from": {"email": settings.SMTP_FROM, "name": "PO Dashboard"},
                "content": [{
                    "type": "text/html",
                    "value": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        <h2 style="color: #4f46e5; text-align: center;">Password Reset Request</h2>
                        <p>Hello,</p>
                        <p>Your verification code is:</p>
                        <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-radius: 6px; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e293b;">{code}</span>
                        </div>
                        <p>This code will expire in 10 minutes.</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                        <p style="font-size: 12px; color: #64748b; text-align: center;">This is an automated message, please do not reply.</p>
                    </div>
                    """
                }]
            })
            headers = {
                'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/v3/mail/send", payload, headers)
            res = conn.getresponse()
            
            if res.status in [200, 201, 202]:
                logger.info(f"Successfully sent SendGrid (HTTP) email to {to_email}")
                return True
            else:
                data = res.read()
                logger.error(f"SendGrid HTTP failed: {res.status} - {data.decode()}")
        except Exception as e:
            logger.error(f"SendGrid HTTP error: {str(e)}")

    # 2. Fallback to SMTP (Works locally)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "Your Password Reset Verification Code"
        msg.attach(MIMEText(f"Your code is {code}", 'plain'))

        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"SMTP error: {str(e)}")
        return False
