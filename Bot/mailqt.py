# from PyQt6.QtWidgets import QApplication
# from qt.LinkExtractorTab import LinkExtractorTab
# from qt.EmailExtractorTab import EmailExtractorTab
# from qt.EmailSenderTab import EmailSenderTab
# from PyQt6.QtWidgets import QTabWidget,QMainWindow
# import sys

# class EmailAutomationApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Email Automation Tool")
#         self.setGeometry(100, 100, 800, 600)

#         # Tab widget
#         self.tabs = QTabWidget()
#         self.setCentralWidget(self.tabs)

#         # Create tab instances
#         self.link_extractor_tab = LinkExtractorTab()
#         self.email_extractor_tab = EmailExtractorTab()
#         self.email_sender_tab = EmailSenderTab()

#         # Add tabs to the main application
#         self.tabs.addTab(self.link_extractor_tab, "Link Extractor")
#         self.tabs.addTab(self.email_extractor_tab, "Email Extractor")
#         self.tabs.addTab(self.email_sender_tab, "Email Sender")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = EmailAutomationApp()
#     window.show()
#     sys.exit(app.exec())













import sys
import asyncio
import random
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from email_extractor import extract_emails_from_link
from run_getemail import process_urls
from conf_log import setup_logging
from driver_setup import setup_driver
from link_extractor import process_links, validate_links
from email_sender import send_email
from email_content import html_content, attachment_path
from utils import read_email_list, stop_program
from fetcher import fetch_emails_from_url
import requests

# Global variables for email extraction
extracted_emails = []
should_stop = False



from PyQt6.QtCore import pyqtSignal, QObject, QThread

class EmailExtractorWorker(QObject):
    finished = pyqtSignal(list)  # Signal to emit when extraction is done
    error = pyqtSignal(str)      # Signal to emit on error

    def extract_emails_from_urls(self, filename):
        """Function to extract emails from the specified URLs file"""
        global extracted_emails, should_stop
        extracted_emails.clear()  # Clear previous results

        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=4) as executor:
            try:
                with open(filename, 'r') as file:
                    urls = list(set(file.read().splitlines()))
                logger_info.info(f"{len(urls)} unique URLs found.")

                with requests.Session() as session:
                    url_cache = {}
                    url_chunks = [urls[i::4] for i in range(4)]
                    executor.map(lambda chunk: process_urls(chunk, session, url_cache), url_chunks)

                # Emit the list of extracted emails
                self.finished.emit(extracted_emails)

            except Exception as e:
                self.error.emit(str(e))

        end_time = time.perf_counter()
        logger_info.info(f"Execution time: {end_time - start_time:.2f} seconds")




class EmailAutomationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Automation Tool")
        self.setGeometry(100, 100, 800, 600)

        # Tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tabs for each functionality
        self.create_link_extractor_tab()
        self.create_email_extractor_tab()  # New tab for extracting emails from URLs
        self.create_email_sender_tab()

    def create_link_extractor_tab(self):
        """Tab for extracting links from search results"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Search input and button
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        layout.addWidget(QLabel("Search Query:"))
        layout.addWidget(self.search_input)

        self.extract_links_button = QPushButton("Extract Links")
        self.extract_links_button.clicked.connect(self.start_link_extraction)
        layout.addWidget(self.extract_links_button)

        # Results display
        self.links_result = QTextEdit()
        layout.addWidget(QLabel("Extracted Links:"))
        layout.addWidget(self.links_result)

        # Save links button
        self.save_links_button = QPushButton("Save Links")
        self.save_links_button.clicked.connect(self.save_links_to_file)
        layout.addWidget(self.save_links_button)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Link Extractor")

    def create_email_extractor_tab(self):
        """Tab for extracting emails from URLs"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.url_file_input = QLineEdit()
        self.url_file_input.setPlaceholderText("Enter filename containing URLs (e.g., urls.txt)")
        layout.addWidget(QLabel("URL List File:"))
        layout.addWidget(self.url_file_input)

        self.extract_emails_button = QPushButton("Extract Emails")
        self.extract_emails_button.clicked.connect(self.start_email_extraction)
        layout.addWidget(self.extract_emails_button)

        # Results display for extracted emails
        self.emails_result = QTextEdit()
        layout.addWidget(QLabel("Extracted Emails:"))
        layout.addWidget(self.emails_result)

        # Save Email button
        self.save_email_button = QPushButton("Save Email")
        self.save_email_button.clicked.connect(self.save_email_to_file)
        layout.addWidget(self.save_email_button)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Email Extractor")

    def create_email_sender_tab(self):
        """Tab for sending emails"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.sender_email_input = QLineEdit()
        self.sender_email_input.setPlaceholderText("Enter your email")
        layout.addWidget(QLabel("Sender Email:"))
        layout.addWidget(self.sender_email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your email password")
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        self.email_file_input = QLineEdit()
        self.email_file_input.setPlaceholderText("Enter path to email list file")
        layout.addWidget(QLabel("Email List File:"))
        layout.addWidget(self.email_file_input)

        self.send_emails_button = QPushButton("Send Emails")
        self.send_emails_button.clicked.connect(self.start_email_sending)
        layout.addWidget(self.send_emails_button)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Email Sender")

    def start_link_extraction(self):
        """Start the link extraction process in a separate thread"""
        search_query = self.search_input.text()
        if search_query:
            self.links_result.setPlainText(f"Extracting links for query: {search_query}...")
            threading.Thread(target=self.extract_links, args=(search_query,), daemon=True).start()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a search query.")

    def extract_links(self, search_query):
        """Function to extract links based on search query"""
        asyncio.run(self.extract_links_async(search_query))

    async def extract_links_async(self, search_query):
        """Asynchronous link extraction using Selenium"""
        driver = setup_driver()
        driver.get("https://www.google.com")

        try:
            # Wait until the search input element is visible and clickable
            input_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "q"))
            )
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

            # Update the UI with the extracted links
            self.links_result.setPlainText("\n".join(links))

        except Exception as e:
            print(f"An error occurred: {e}")
            driver.save_screenshot("error_screenshot.png")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        
        finally:
            driver.quit()  # Close the browser after finishing

    def save_links_to_file(self):
        """Save extracted links to a file with a custom name"""
        links = self.links_result.toPlainText()
        if not links:
            QMessageBox.warning(self, "No Links", "There are no links to save.")
            return

        # Ask the user for the filename using an input dialog
        file_name, ok = QInputDialog.getText(self, "Input Dialog", "Enter the filename to save (e.g., myfile.txt):")
        
        if ok and file_name:  # Check if the user clicked OK and provided a filename
            file_name = file_name.strip()  # Strip any whitespace
            if not file_name.endswith('.txt'):  # Ensure the file has a .txt extension
                file_name += '.txt'
            try:
                with open(file_name, "w") as file:
                    file.write(links)
                QMessageBox.information(self, "Success", "Links saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving the file: {e}")

    def start_email_sending(self):
        """Start the email sending process in a separate thread"""
        sender_email = self.sender_email_input.text()
        password = self.password_input.text()
        email_file = self.email_file_input.text()

        if sender_email and password and email_file:
            threading.Thread(target=self.send_emails, args=(sender_email, password, email_file), daemon=True).start()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")

    def send_emails(self, sender_email, password, email_file):
        """Function to send emails to extracted email addresses"""
        asyncio.run(self.send_emails_async(sender_email, password, email_file))

    async def send_emails_async(self, sender_email, password, email_file):
        """Asynchronous email sending"""
        try:
            email_list = await read_email_list(email_file)
            tasks = []
            for receiver_email in email_list:
                tasks.append(send_email(
                    receiver_email=receiver_email,
                    html_content=html_content,
                    sender_email=sender_email,
                    password=password,
                    attachment_path=attachment_path
                ))
            
            await asyncio.gather(*tasks)  # Send emails concurrently
            QMessageBox.information(self, "Success", "Emails sent successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while sending emails: {e}")

    def start_email_extraction(self):
        """Start the email extraction process in a separate thread"""
        filename = self.url_file_input.text()
        
        if filename:
            self.worker = EmailExtractorWorker()
            self.worker.finished.connect(self.update_email_results)  # Connect to update method
            self.worker.error.connect(self.show_error_message)  # Connect to error method

            self.thread = QThread()
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(lambda: self.worker.extract_emails_from_urls(filename))  # Start extraction
            self.thread.start()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a filename containing URLs.")

    def update_email_results(self, emails):
        """Update the UI with the extracted emails"""
        if emails:
            self.emails_result.setPlainText("\n".join(emails))
        else:
            self.emails_result.setPlainText("No emails found.")
        self.thread.quit()  # Quit the thread after finishing
        self.thread.wait()  # # Wait for the thread to finish

    def show_error_message(self, message):
        """Show an error message"""
        QMessageBox.critical(self, "Error", message)
        self.thread.quit()  # Quit the thread on error
        self.thread.wait()  # Wait for the thread to finish

    def save_email_to_file(self):
        """Save extracted emails to a file with a custom name"""
        emails = self.emails_result.toPlainText()
        if not emails:
            QMessageBox.warning(self, "No Emails", "There are no emails to save.")
            return

        file_name, ok = QInputDialog.getText(self, "Input Dialog", "Enter the filename to save (e.g., myfile.txt):")
        
        if ok and file_name:
            file_name = file_name.strip()
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            try:
                with open(file_name, "w") as file:
                    file.write(emails)
                QMessageBox.information(self, "Success", "Emails saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving the file: {e}")
   
   
    def some_gui_function(self):
        url = self.url_input.text()  # Get the URL from the GUI
        filename = self.url_file_input.text()  # Get the filename from the GUI input
        extracted_emails = []

        # Call the extraction function and get the emails
        emails = extract_emails_from_link(url, extracted_emails, filename)

        # Update the GUI with the extracted emails
        if emails:
            self.emails_result.setPlainText("\n".join(emails))
        else:
            self.emails_result.setPlainText("No emails found.")


    def extract_emails_from_urls(self, filename):
        """Function to extract emails from the specified URLs file"""
        global extracted_emails, should_stop

        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=4) as executor:  # Define thread pool size
            # Read and deduplicate URLs
            try:
                with open(filename, 'r') as file:
                    urls = list(set(file.read().splitlines()))
                logger_info.info(f"{len(urls)} unique URLs found.")

                # Create a shared session and cache for URLs
                with requests.Session() as session:
                    url_cache = {}  # Define cache for URLs
                    # Split URLs across threads
                    url_chunks = [urls[i::4] for i in range(4)]  # Divide URLs for 4 threads
                    executor.map(lambda chunk: process_urls(chunk, session, url_cache), url_chunks)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while reading URLs: {e}")
                return

        end_time = time.perf_counter()
        logger_info.info(f"Execution time: {end_time - start_time:.2f} seconds")
        self.emails_result.setPlainText("\n".join(extracted_emails))  # Display extracted emails


if __name__ == "__main__":
    setup_logging()
    logger_info = logging.getLogger('info')
    logger_info.info("This is an info message.")
    app = QApplication(sys.argv)
    # print(f"Saving to: {SAVE_FILE_PATH}")  #
    window = EmailAutomationApp()
    window.show()
    sys.exit(app.exec())
