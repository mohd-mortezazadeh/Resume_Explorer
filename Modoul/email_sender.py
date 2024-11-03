# email_sender.py

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils import read_email_list

smtp_server = "smtp.gmail.com"
port = 587  # For starttls

def send_email(receiver_email, html_content, sender_email, password, subject="Data Scientist | Full Stack Developer", attachment_path=None):
    """Send an email with optional attachment."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(html_content, "html"))

    # Attach file if specified
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {attachment_path}")
        message.attach(part)

    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print(f"Error sending email to {receiver_email}: {e}")
    finally:
        server.quit()
