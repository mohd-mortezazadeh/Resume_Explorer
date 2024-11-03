# link_extractor.py

import asyncio
import aiohttp
from selenium.webdriver.common.by import By
from config import EXCLUDE_LINKS_START, SAVE_FILE_PATH

async def is_valid_url(session, url):
    """Check if the URL returns a valid response."""
    try:
        async with session.head(url, allow_redirects=True) as response:
            return response.status < 400
    except Exception:
        return False

async def validate_links(urls):
    """Validate multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [is_valid_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return {url for url, valid in zip(urls, results) if valid}

def process_links(driver):
    """Extract and process links from the current page."""
    current_links = []
    for a in driver.find_elements(By.XPATH, './/a'):
        href = a.get_attribute('href')
        if href and not any(href.startswith(link) for link in EXCLUDE_LINKS_START):
            current_links.append(href)
    return current_links

def save_links(links):
    """Save the extracted links to a file."""
    with open(SAVE_FILE_PATH, "w") as w:
        w.write('\n'.join(links))
