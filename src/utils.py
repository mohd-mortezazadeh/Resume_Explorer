# utils.py

import os
import asyncio
import logging
import random
import aiofiles
from driver_setup import setup_driver
from link_extractor import process_links, validate_links, save_links
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Create a logger instance
logger_info = logging.getLogger(__name__)

def save_email(email_address, file_name):
    """Save the extracted email to a file."""
    try:
        with open('swadenmail.txt', 'a') as email_file:
            email_file.write(email_address + '\n')
        logger_info.info(f"Saved email: {email_address}")
    except Exception as e:
        logger_info.error(f"Error saving email {email_address}: {e}")
        
        
def stop_program():
    """Stop the email extraction process."""
    global should_stop
    should_stop = True
    

async def read_email_list(file_path):
    """Read email addresses from file and return them as a list."""
    if not os.path.exists(file_path):
        logger_info.error(f"File not found: {file_path}")
        return []

    try:
        async with aiofiles.open(file_path, mode='r') as f:
            return [line.strip() for line in await f.readlines()]
    except Exception as e:
        logger_info.error(f"Error reading file {file_path}: {e}")
        return []


async def scroll_and_load_nav_shared(file_name):
    driver = setup_driver()
    driver.get("https://www.google.com")

    search_query = input("What is your search?\n")
    
    try:
        # Wait until the search input element is visible and clickable
        input_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "q"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", input_element)  # Scroll to element
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "q")))

        # Send search query
        input_element.send_keys(search_query)
        input_element.submit()
        
        links = set()  # To store unique valid links
        page_num = 1   # Track page number

        while True:
            print(f"Processing page {page_num}...")  # Log current page number
            
            # Scroll to the bottom to make sure all elements are loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)  # Wait for potential new elements to load

            # Extract and validate links
            current_links = process_links(driver)
            valid_links = await validate_links(current_links)
            links.update(valid_links)

            # Save links to file
            await save_links(links,file_name)  # Make sure to await this

            # Add a small random delay
            await asyncio.sleep(random.uniform(1, 3))

            # Try to go to the next page
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, 'pnnext'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                
                # Add another random delay after clicking "Next"
                await asyncio.sleep(random.uniform(1, 3))
                
                page_num += 1  # Increment page number

            except Exception:
                print("No more pages to navigate.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optional: Capture screenshot for debugging
        driver.save_screenshot("error_screenshot.png")
        
    finally:
        driver.quit()  # Close the browser after finishing




