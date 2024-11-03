import time
import requests
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from extract_emails import EmailExtractor
from extract_emails.browsers import RequestsBrowser
import logging

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%Y %H:%M:%S',
    level=logging.INFO
)
logger_info = logging.getLogger('info')
logger_error = logging.getLogger('error')

extracted_emails = []
should_stop = False

def fetch_emails_from_url(url):
    """Fetch emails from a given URL."""
    global extracted_emails

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'}
        response = requests.get(url, headers=headers, timeout=2)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

            for link in links:
                href = link.get("href")
                if href:
                    extract_emails_from_link(href)

    except requests.exceptions.RequestException as req_err:
        logger_error.error(f"Request error: {req_err} - {current_thread().name}")
    except Exception as err:
        logger_error.error(f"General error: {err} - {current_thread().name}")

def extract_emails_from_link(link):
    """Extract emails from a given link."""
    global extracted_emails

    with RequestsBrowser() as browser:
        email_extractor = EmailExtractor(link, browser, depth=2)
        emails = email_extractor.get_emails()

        for email in emails:
            email_address = email.as_dict()["email"]
            if email_address not in extracted_emails:
                extracted_emails.append(email_address)
                save_email(email_address)

def save_email(email_address):
    """Save the extracted email to a file."""
    with open('Emails/SaveEmail.txt', 'a') as email_file:
        email_file.write(email_address + '\n')
    print(f"{email_address} - {current_thread().name}")
    logger_info.info(f"{email_address} - {current_thread().name}")

def foo(name):
    """Main function to process URLs and extract emails."""
    global should_stop

    with open('Urls/saveurl.txt', 'r') as file:
        urls = file.readlines()

    for url in urls:
        if should_stop:
            break
        fetch_emails_from_url(url.strip())

def stop_program():
    """Stop the email extraction process."""
    global should_stop
    should_stop = True

if __name__ == "__main__":
    start_time = time.perf_counter()

    with ThreadPoolExecutor() as executor:
        thread_names = ["one", "two", "three", "four", 'five', 'six', 'seven', 'eight', 'nine']
        executor.map(foo, thread_names)

    stop_program()

    end_time = time.perf_counter()
    print("Execution time:", end_time - start_time, current_thread().name)