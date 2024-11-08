# email_extractor.py

from extract_emails import EmailExtractor
from extract_emails.browsers import RequestsBrowser
import logging
from utils import save_email
from threading import Lock

logger_info = logging.getLogger('info')
extracted_emails = []
extraction_lock = Lock()  # Create a lock for thread safety

def extract_emails_from_link(link, filename):
    """Extract emails from a given link."""
    with RequestsBrowser() as browser:
        email_extractor = EmailExtractor(link, browser, depth=1)
        emails = email_extractor.get_emails()

        for email in emails:
            email_address = email.as_dict()["email"]
            with extraction_lock:  # Acquire the lock before modifying the list
                if email_address not in extracted_emails:
                    extracted_emails.append(email_address)
                    save_email(email_address, file_name=filename)  # Save email
                    logger_info.info(f"Extracted email: {email_address}")

    return extracted_emails  # Return the list of extracted emails


