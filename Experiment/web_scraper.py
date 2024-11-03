# web_scraper.py
import asyncio
import aiohttp
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt6.QtCore import QThread, pyqtSignal

# List of excluded links for web scraping
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
    "https://www.linkedin.com"
]

class ScraperThread(QThread):
    update_results = pyqtSignal(str)
    finished_scraping = pyqtSignal(set, str)

    def __init__(self, search_query, filename):
        super().__init__()
        self.search_query = search_query
        self.filename = filename
        self.driver = None

    def run(self):
        self.driver = self.setup_driver()
        self.run_scraper(self.search_query)

    def setup_driver(self):
        service = Service("./chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(service=service, options=options)

    async def is_valid_url(self, session, url):
        try:
            async with session.head(url, allow_redirects=True) as response:
                return response.status < 400
        except Exception:
            return False

    async def validate_links(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.is_valid_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return {url for url, valid in zip(urls, results) if valid}

    def process_links(self):
        current_links = []
        for a in self.driver.find_elements(By.XPATH, './/a'):
            href = a.get_attribute('href')
            if href and not any(href.startswith(link) for link in exclude_links_start):
                current_links.append(href)
        return current_links

    def run_scraper(self, search_query):
        try:
            self.driver.get("https://www.google.com")
            input_element = self.driver.find_element(By.NAME, "q")
            input_element.send_keys(search_query)
            input_element.submit()

            links = set()
            while True:
                current_links = self.process_links()
                valid_links = asyncio.run(self.validate_links(current_links))
                links.update(valid_links)

                self.update_results.emit("\n".join(valid_links))

                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'pnnext'))
                    )
                    element.click()
                except Exception:
                    break

            # Emit finished signal with valid links and filename
            self.finished_scraping.emit(links, os.path.join(os.getcwd(), self.filename))

        except Exception as e:
            self.update_results.emit(f"An error occurred: {e}")
        finally:
            self.driver.quit()