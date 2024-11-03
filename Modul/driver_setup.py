# driver_setup.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import CHROMEDRIVER_PATH, HEADLESS_MODE

def setup_driver():
    """Initialize and configure the WebDriver."""
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    # if HEADLESS_MODE:
    #     options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver
