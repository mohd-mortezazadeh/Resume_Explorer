# main.py

import asyncio
from email_sender import send_email
from email_content import html_content, attachment_path
from utils import read_email_list
from conf_log import setup_logging

sender_email = input("what is your email:\n")
password = input("Enter your email password:\n")

async def main_sender_email():
    EMAIL_LINK_FILE = input("what is your email file?\n")
    email_list = await read_email_list(EMAIL_LINK_FILE)
    tasks = []
    for receiver_email in email_list:
        tasks.append(send_email(
            receiver_email=receiver_email,
            html_content=html_content,
            sender_email=sender_email,
            password=password,
            attachment_path=attachment_path
        ))
    
    await asyncio.gather(*tasks)  # ارسال همزمان ایمیل‌ها

if __name__ == "__main__":
    setup_logging()  # Ensure logging is set up
    asyncio.run(main_sender_email())