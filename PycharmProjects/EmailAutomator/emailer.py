import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import os
from config import SENDER_EMAIL, SENDER_NAME, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(to_email, subject, html_body, attachments=None):
    if not SENDER_PASSWORD:
        raise ValueError("Gmail password not found in environment variables")
        
    msg = MIMEMultipart()
    msg['From'] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    if attachments:
        for file_path in attachments:
            try:
                if not os.path.exists(file_path):
                    print(f"[WARNING] Attachment file not found: {file_path}")
                    continue
                    
                part = MIMEBase('application', 'octet-stream')
                with open(file_path, 'rb') as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                msg.attach(part)
                print(f"[SUCCESS] Attached file: {file_path}")
            except Exception as e:
                print(f"[ERROR] Failed to attach {file_path}: {str(e)}")

    try:
        print(f"[INFO] Connecting to {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("[INFO] Starting TLS connection")
            server.starttls()
            print("[INFO] Attempting login")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print(f"[INFO] Sending email to {to_email}")
            server.send_message(msg)
        print(f"[SUCCESS] Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] SMTP Authentication failed. Please check your Gmail password.")
        raise
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP error occurred: {str(e)}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending email: {str(e)}")
        raise
