"""
Email service for sending OTP verification emails
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "").replace(" ", "")


def send_otp_email(recipient_email: str, otp: str, account_holder_name: str = "Valued Customer") -> bool:
    """
    Send an OTP verification email.

    Args:
        recipient_email: Destination email address
        otp: 6-digit OTP code
        account_holder_name: Name to display in the email

    Returns:
        True if sent successfully, False otherwise
    """
    if not EMAIL_USER or not EMAIL_APP_PASSWORD:
        logger.error("Email credentials not configured in .env")
        return False

    subject = "Smart Bank – Your Verification Code"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8"/>
      <style>
        body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
        .wrapper {{ max-width: 480px; margin: 40px auto; background: #fff;
                    border-radius: 12px; overflow: hidden;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg,#1d4ed8,#2563eb);
                   padding: 32px 28px; text-align: center; }}
        .header h1 {{ color: #fff; margin: 0; font-size: 22px; letter-spacing: 0.5px; }}
        .header p  {{ color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 13px; }}
        .body {{ padding: 32px 28px; }}
        .body p {{ color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }}
        .otp-box {{ background: #eff6ff; border: 2px dashed #3b82f6;
                    border-radius: 10px; text-align: center; padding: 20px; margin: 24px 0; }}
        .otp-code {{ font-size: 38px; font-weight: 700; letter-spacing: 12px;
                     color: #1d4ed8; font-family: monospace; }}
        .otp-exp {{ font-size: 13px; color: #6b7280; margin-top: 8px; }}
        .footer {{ background: #f9fafb; padding: 16px 28px; text-align: center;
                   font-size: 12px; color: #9ca3af; border-top: 1px solid #e5e7eb; }}
      </style>
    </head>
    <body>
      <div class="wrapper">
        <div class="header">
          <h1>🏦 Smart Bank</h1>
          <p>Account Verification</p>
        </div>
        <div class="body">
          <p>Hello <strong>{account_holder_name}</strong>,</p>
          <p>We received a request to verify your identity on Smart Banking Assistant.
             Use the code below to complete verification:</p>
          <div class="otp-box">
            <div class="otp-code">{otp}</div>
            <div class="otp-exp">⏱ This code expires in <strong>5 minutes</strong></div>
          </div>
          <p>If you did not request this code, please ignore this email.
             Never share this code with anyone.</p>
          <p>Stay secure,<br/><strong>Smart Bank Security Team</strong></p>
        </div>
        <div class="footer">
          © 2026 Smart Bank · This is an automated message, please do not reply.
        </div>
      </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Smart Bank <{EMAIL_USER}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_APP_PASSWORD)
            smtp.sendmail(EMAIL_USER, recipient_email, msg.as_string())

        logger.info(f"OTP email sent to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed – check EMAIL_USER / EMAIL_APP_PASSWORD in .env")
        return False
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}", exc_info=True)
        return False
