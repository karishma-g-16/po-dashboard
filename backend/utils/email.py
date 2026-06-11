import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

logger = logging.getLogger(__name__)

def send_reset_code_email(to_email: str, code: str):
    """
    Send a password reset verification code via email.
    Prioritizes SendGrid API (better for Render), falls back to SMTP.
    """
    # 1. Try SendGrid first (Recommended for Render)
    if settings.SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=settings.SMTP_FROM,
                to_emails=to_email,
                subject='Your Password Reset Verification Code',
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h2 style="color: #4f46e5; text-align: center;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password for your PO Management Dashboard account.</p>
                    <p>Please use the following verification code to proceed:</p>
                    <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-radius: 6px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e293b;">{code}</span>
                    </div>
                    <p>This code will expire in 10 minutes.</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #64748b; text-align: center;">This is an automated message, please do not reply.</p>
                </div>
                """
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent SendGrid email to {to_email}")
                return True
            else:
                logger.error(f"SendGrid failed with status code {response.status_code}")
        except Exception as sg_e:
            logger.error(f"SendGrid error: {str(sg_e)}")
            # If SendGrid fails, we continue to try SMTP fallback

    # 2. Fallback to SMTP (Works locally, but likely fails on Render)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("No email credentials configured (SendGrid or SMTP).")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "Your Password Reset Verification Code"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h2 style="color: #4f46e5;">Password Reset</h2>
                    <p>Your verification code is: <strong>{code}</strong></p>
                    <p>This code will expire in 10 minutes.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Standard SMTP logic
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"Successfully sent SMTP email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"All email methods failed for {to_email}: {str(e)}")
        return False
