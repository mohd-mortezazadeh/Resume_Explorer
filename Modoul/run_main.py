# main.py

import asyncio
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from driver_setup import setup_driver
from link_extractor import process_links, validate_links, save_links

def main():
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
            time.sleep(2)  # Wait for potential new elements to load

            # Extract and validate links
            current_links = process_links(driver)
            valid_links = asyncio.run(validate_links(current_links))
            links.update(valid_links)

            # Save links to file
            save_links(links)

            # Add a small random delay
            time.sleep(random.uniform(1, 3))

            # Try to go to the next page
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, 'pnnext'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                
                # Add another random delay after clicking "Next"
                time.sleep(random.uniform(1, 3))
                
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

if __name__ == "__main__":
    main()
