import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

def send_reset_code_email(to_email: str, code: str):
    """
    Send a password reset verification code via email.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error(f"SMTP credentials not configured. Cannot send email to {to_email}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "Your Password Reset Verification Code"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h2 style="color: #4f46e5; text-align: center;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password for your PO Management Dashboard account.</p>
                    <p>Please use the following verification code to proceed with resetting your password:</p>
                    <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-radius: 6px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e293b;">{code}</span>
                    </div>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #64748b; text-align: center;">This is an automated message, please do not reply.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        if settings.SMTP_PORT == 465:
            # Use SSL/TLS for port 465
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587 or others
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"Successfully sent reset code email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
