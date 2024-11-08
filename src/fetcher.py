import requests
from bs4 import BeautifulSoup
from email_extractor import extract_emails_from_link
import logging
from threading import current_thread
import time
from email_extractor import extraction_lock, extracted_emails


logger_info = logging.getLogger('info')
logger_error = logging.getLogger('error')

def fetch_emails_from_url(url, session, url_cache, filename=None, retries=3):
    logger_info.info(f"Fetching emails from URL: {url} - Thread: {current_thread().name}")
    
    if not url.strip():  # Validate URL
        logger_error.error("Empty URL provided, skipping...")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
    }

    try:
        logger_info.info(f"Making request to: {url}")
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Check for HTTP errors

        if response.status_code == 200:
            logger_info.info(f"Successfully fetched data from: {url}")
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")
            emails = []

            for link in links:
                href = link.get("href")
                if href and (href.startswith("http://") or href.startswith("https://")):
                    logger_info.info(f"Processing link: {href}")
                    email_links = extract_emails_from_link(href, filename)
                    with extraction_lock:  # Lock when modifying the global list
                        for email in email_links:
                            if email not in extracted_emails:
                                extracted_emails.append(email)
                                emails.append(email)

            url_cache[url] = emails
            logger_info.info(f"Cached emails for URL: {url}")

        else:
            logger_error.error(f"Failed to fetch {url}: Status code {response.status_code}")

    except requests.exceptions.RequestException as req_err:
        logger_error.error(f"Request error: {req_err} - {current_thread().name}")
        if retries > 0:
            logger_info.info(f"Retrying {url} ({3 - retries + 1}/3)")
            time.sleep(2)
            fetch_emails_from_url(url, session, url_cache, filename, retries - 1)
    except Exception as err:
        logger_error.error(f"General error: {err} - {current_thread().name}")
