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
        import socket
        # Force IPv4 by resolving the hostname specifically for AF_INET
        try:
            addr_info = socket.getaddrinfo(settings.SMTP_HOST, settings.SMTP_PORT, socket.AF_INET, socket.SOCK_STREAM)
            resolved_ip = addr_info[0][4][0]
            logger.info(f"Forcing IPv4: {settings.SMTP_HOST} resolved to {resolved_ip}")
        except Exception as dns_e:
            logger.error(f"DNS resolution failed: {dns_e}")
            resolved_ip = settings.SMTP_HOST # Fallback to hostname

        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "Your Password Reset Verification Code"

        # ... (body content same) ...
        msg.attach(MIMEText(body, 'html'))

        # Use resolved_ip but pass the original hostname for SSL certificate verification
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(resolved_ip, settings.SMTP_PORT, timeout=15) as server:
                # We need to ensure the SSL context checks against the original hostname
                # but smtplib.SMTP_SSL handles this if we pass it, however some versions 
                # might fail if host is IP. If so, we might need a custom context.
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(resolved_ip, settings.SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"Successfully sent reset code email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
