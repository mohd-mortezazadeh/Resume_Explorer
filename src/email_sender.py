# email_sender.py

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils import logger_info

smtp_server = "smtp.gmail.com"
port = 587  # For starttls

async def send_email(receiver_email, html_content, sender_email, password, subject="Data Scientist | Full Stack Developer", attachment_path=None):
    """Send an email with optional attachment."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(html_content, "html"))

    # Attach file if specified
    if attachment_path:
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {attachment_path.split('/')[-1]}")
            message.attach(part)
        except Exception as e:
            logger_info.error(f"Error attaching file {attachment_path}: {e}")
            return  # Exit if there's an error attaching the file

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger_info.info(f"Email sent to {receiver_email}")
    except smtplib.SMTPException as e:
        logger_info.error(f"SMTP error sending email to {receiver_email}: {e}")
    except Exception as e:
        logger_info.error(f"Error sending email to {receiver_email}: {e}")
