# link_extractor.py

import asyncio
import aiohttp
import aiofiles
from selenium.webdriver.common.by import By
from config import EXCLUDE_LINKS_START, SAVE_FILE_PATH

# دیکشنری کش برای ذخیره نتایج اعتبارسنجی
cache = {}

async def is_valid_url(session, url):
    """Check if the URL returns a valid response, using cache if available."""
    # اگر نتیجه در کش موجود باشد، از آن استفاده کنید
    if url in cache:
        return cache[url]
    
    try:
        async with session.head(url, allow_redirects=True) as response:
            valid = response.status < 400
            # ذخیره نتیجه در کش
            cache[url] = valid
            return valid
    except Exception:
        cache[url] = False  # در صورت بروز خطا، نتیجه را در کش ذخیره کنید
        return False

async def validate_links(urls):
    """Validate multiple URLs concurrently, using caching."""
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

async def save_links(links):
    """Save the extracted links to a file asynchronously."""
    try:
        async with aiofiles.open(SAVE_FILE_PATH, "w") as w:
            await w.write('\n'.join(links))
    except Exception as e:
        print(f"Error saving links: {e}")