# fetcher.py

import requests
from bs4 import BeautifulSoup
from email_extractor import extract_emails_from_link
import logging
from threading import current_thread

logger_error = logging.getLogger('error')

def fetch_emails_from_url(url, extracted_emails):
    """Fetch emails from a given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'}
        response = requests.get(url, headers=headers, timeout=2)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

            for link in links:
                href = link.get("href")
                if href:
                    extract_emails_from_link(href, extracted_emails)

    except requests.exceptions.RequestException as req_err:
        logger_error.error(f"Request error: {req_err} - {current_thread().name}")
    except Exception as err:
        logger_error.error(f"General error: {err} - {current_thread().name}")
