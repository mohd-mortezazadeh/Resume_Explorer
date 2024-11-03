# main.py

from email_sender import send_email
from email_content import html_content, attachment_path
from utils import read_email_list

sender_email = "siyamak1981@gmail.com"
password = input("Enter your email password: ")

def main():
    email_list = read_email_list("SaveEmail.txt")
    for receiver_email in email_list:
        send_email(
            receiver_email=receiver_email,
            html_content=html_content,
            sender_email=sender_email,
            password=password,
            attachment_path=attachment_path
        )
        print(f"Email sent to {receiver_email}")

if __name__ == "__main__":
    main()
