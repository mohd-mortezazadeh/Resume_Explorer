import time
import requests
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from extract_emails import EmailExtractor
from extract_emails.browsers import RequestsBrowser
import logging
import os

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


def fetch_emails_from_url(url, output_file):
    """Fetch emails from a given URL."""
    global extracted_emails

    if not url:  # Check if the URL is empty
        logger_error.error("Received empty URL.")
        return

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

            for link in links:
                href = link.get("href")
                if href:
                    full_link = requests.compat.urljoin(url, href)  # Ensure full URL is formed
                    logger_info.info(f"Fetching emails from link: {full_link}")  # Log the full link
                    extract_emails_from_link(full_link, output_file)  # Pass output_file here
        else:
            logger_error.error(f"Failed to retrieve {url}: Status code {response.status_code}")

    except requests.exceptions.RequestException as req_err:
        logger_error.error(f"Request error: {req_err} - {current_thread().name}")
    except Exception as err:
        logger_error.error(f"General error: {err} - {current_thread().name}")

def extract_emails_from_link(link, output_file):
    """Extract emails from a given link."""
    global extracted_emails

    with RequestsBrowser() as browser:
        logger_info.info(f"Fetching emails from link: {link}")
        email_extractor = EmailExtractor(link, browser, depth=2)
        emails = email_extractor.get_emails()

        if not emails:
            logger_info.warning(f"No emails found at: {link}")  # Log if no emails found
            # If you want to log the content, you can do so by fetching it directly from the requests response
            # or by using a different method to fetch the content if necessary.

        for email in emails:
            email_address = email.as_dict()["email"]
            if email_address not in extracted_emails:
                extracted_emails.append(email_address)
                save_email(email_address, output_file)  # Pass output_file here

                
def save_email(email_address, output_file):
    """Save the extracted email to a specified file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'a') as email_file:
        email_file.write(email_address + '\n')
    print(f"{email_address} - {current_thread().name}")
    logger_info.info(f"{email_address} - {current_thread().name}")

def foo(url_file, output_file):
    """Main function to process URLs and extract emails."""
    global should_stop

    with open(url_file, 'r') as file:
        urls = file.readlines()

    for url in urls:
        if should_stop:
            break
        fetch_emails_from_url(url.strip(), output_file)  # Pass output_file here

def stop_program():
    """Stop the email extraction process."""
    global should_stop
    should_stop = True

def start_email_extraction(url_file, output_file):
    """Start the email extraction process using multiple threads."""
    global extracted_emails
    extracted_emails.clear()  # Clear previous emails

    # Check if the URL file exists
    if not os.path.isfile(url_file):
        logger_error.error(f"URL file not found: {url_file}")
        return

  

    # Delete the existing output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        logger_info.info(f"Deleted existing file: {output_file}")

    start_time = time.perf_counter()

    try:
        with ThreadPoolExecutor() as executor:
            thread_names = ["one", "two", "three", "four", 'five', 'six', 'seven', 'eight', 'nine']
            # Pass url_file and output_file to foo
            executor.map(lambda name: foo(url_file, output_file), thread_names)
    except Exception as e:
        logger_error.error(f"An error occurred during thread execution: {e}")

    stop_program()

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    logger_info.info(f"Execution time: {execution_time:.2f} seconds - {current_thread().name}")