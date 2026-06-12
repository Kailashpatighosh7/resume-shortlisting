"""
SMTP Client
============
Gmail SMTP integration for sending emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_email(
    recipient_email: str,
    subject: str,
    html_body: str,
) -> bool:
    """
    Send an email via Gmail SMTP.

    Args:
        recipient_email: Recipient's email address.
        subject: Email subject line.
        html_body: HTML content of the email.

    Returns:
        True if sent successfully, False otherwise.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("⚠️ SMTP not configured. Email not sent.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.SMTP_FROM_EMAIL, recipient_email, msg.as_string()
            )

        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
