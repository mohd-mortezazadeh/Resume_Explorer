# email_extractor.py

from extract_emails import EmailExtractor
from extract_emails.browsers import RequestsBrowser
import logging
from utils import save_email

logger_info = logging.getLogger('info')

filename = input("Enter the filename to save (e.g., myfile.txt): ")


def extract_emails_from_link(link, extracted_emails):
    """Extract emails from a given link."""
    with RequestsBrowser() as browser:
        email_extractor = EmailExtractor(link, browser, depth=1)
        emails = email_extractor.get_emails()

        for email in emails:
            email_address = email.as_dict()["email"]
            if email_address not in extracted_emails:
                extracted_emails.append(email_address)
                save_email(email_address, file_name=filename)
                logger_info.info(f"Extracted email: {email_address}")
