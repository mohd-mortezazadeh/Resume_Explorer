import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import asyncio
import aiohttp

# Setup WebDriver using Service
service = Service("./chromedriver")
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without a UI (optional)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")

print(driver.title)
search_query = input('What is your search?\n')
input_element = driver.find_element(By.NAME, "q")
input_element.send_keys(search_query)
input_element.submit()

# List of excluded links
exclude_links_start = [
    "https://www.aparat.com/",
    "https://www.google.com/",
    "https://consent.yahoo.com/",
    "https://support.google.com/",
    "https://policies.google.com/",
    "https://myactivity.google.com/",
    "https://accounts.google.com/",
    "https://webcache.googleusercontent.com/",
    "https://en.wikipedia.org/",
    "https://www.youtube.com/",
    "https://en.m.wikipedia.org/",
    "https://telegram.me/",
    "http://webcache.googleusercontent.com/",
    "https://translate.google.com/",
    "https://www.indeed.com/",
    "https://www.googleadservices.com/",
    "https://www.glassdoor.com/",
    "javascript:void(0)",
    "mailto:?body",
    "https://mail.google.com/",
    "https://www.bbc.com/",
    "https://instagram.com/",
    "https://github.com/",
    "https://www.glassdoor.co.in",
    "https://www.quora.com",
    "https://www.linkedin.com",
    "https://www.pinterest.com/"
]

links = set()  # Use a set to avoid duplicate links

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
    """Extract and process links."""
    current_links = []
    for a in driver.find_elements(By.XPATH, './/a'):
        href = a.get_attribute('href')
        if href and not any(href.startswith(link) for link in exclude_links_start):
            current_links.append(href)
    return current_links

try:
    while True:
        # Extract links
        current_links = process_links(driver)

        # Validate URLs asynchronously
        valid_links = asyncio.run(validate_links(current_links))

        links.update(valid_links)  # Add valid links to the set
        
        # Save links to file
        with open("Urls/saveurl.txt", "w") as w:
            w.write('\n'.join(links))

        # Go to the next page
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'pnnext'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            time.sleep(2)  # Delay to allow the page to load
        except Exception:
            print("No more pages to navigate.")
            break
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()  # Close the browser after finishing