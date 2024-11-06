import time
from concurrent.futures import ThreadPoolExecutor
from fetcher import fetch_emails_from_url
from utils import stop_program
import logging
import requests
from conf_log import setup_logging
# Logging configuration




extracted_emails = []
should_stop = False


def process_urls(urls, session, url_cache):
    """Process URLs to extract emails with optimization."""
    global should_stop

    for url in urls:
        if should_stop:
            break
        fetch_emails_from_url(url.strip(), extracted_emails, session, url_cache)

def main(filename):
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=4) as executor:  # Define thread pool size
        # Read and deduplicate URLs
        with open(filename, 'r') as file:
            urls = list(set(file.read().splitlines()))
        logger_info.info(f"{len(urls)} unique URLs found.")

        # Create a shared session and cache for URLs
        with requests.Session() as session:
            url_cache = {}  # تعریف کش برای URL ها
            # Split URLs across threads
            url_chunks = [urls[i::4] for i in range(4)]  # Divide URLs for 4 threads
            executor.map(lambda chunk: process_urls(chunk, session, url_cache), url_chunks)

    stop_program()
    end_time = time.perf_counter()
    logger_info.info(f"Execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    setup_logging()
    filename=input("Enter the filename containing URLs (e.g., urls.txt):")
    logger_info = logging.getLogger('info')
    logger_info.info("This is an info message.")
    main(filename)
