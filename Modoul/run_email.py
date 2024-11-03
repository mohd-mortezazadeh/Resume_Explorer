# main.py

import time
from concurrent.futures import ThreadPoolExecutor
from fetcher import fetch_emails_from_url
from utils import stop_program
import logging

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%Y %H:%M:%S',
    level=logging.INFO
)
logger_info = logging.getLogger('info')

extracted_emails = []
should_stop = False

def process_urls(thread_name):
    """Main function to process URLs and extract emails."""
    global should_stop

    with open('saveurls.txt', 'r') as file:
        urls = file.readlines()

    for url in urls:
        if should_stop:
            break
        fetch_emails_from_url(url.strip(), extracted_emails)

if __name__ == "__main__":
    start_time = time.perf_counter()

    with ThreadPoolExecutor() as executor:
        thread_names = ["one", "two", "three", "four", 'five', 'six', 'seven', 'eight', 'nine']
        executor.map(process_urls, thread_names)

    stop_program()

    end_time = time.perf_counter()
    print("Execution time:", end_time - start_time)
