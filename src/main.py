
import sys
import asyncio
import random
import threading
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QInputDialog
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from run_getemail import process_urls
from conf_log import setup_logging
from driver_setup import setup_driver
from link_extractor import process_links, validate_links
from email_sender import send_email
from email_content import html_content
from utils import read_email_list
from email_extractor import extracted_emails
from PyQt6.QtCore import QThread, pyqtSignal, QObject





class EmailAutomationApp(QMainWindow):
    log_signal = pyqtSignal(str)  
    def __init__(self):
        super().__init__()
        self.log_signal.connect(self.update_log_output)  # اتصال سیگنال به متد
        self.setWindowTitle("Email Automation Tool")
        self.setGeometry(100, 100, 800, 600)

        # Tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # ======================start tabs=========================
        # Tabs for each functionality
        self.create_link_extractor_tab()
        self.create_email_extractor_tab()  # New tab for extracting emails from URLs
        self.create_email_sender_tab()
    #============================signals=======================
    def update_log_output(self, message):
        self.log_output.append(message)  # به روز رسانی لاگ در ترد اصلی
    # ==========================================================
    # =======================end tab===============================
    # ================== start tab ==================
    def create_link_extractor_tab(self):
        """Tab for extracting links from search results"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)  # Set minimal spacing between widgets
        layout.setContentsMargins(10, 10, 10, 10)  # Set margins (left, top, right, bottom)

        # Search input and button
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)  #
        self.search_input.setPlaceholderText("Enter search query...")
        layout.addWidget(QLabel("Search Query:"))
        layout.addWidget(self.search_input)

        self.extract_links_button = QPushButton("Extract Links")
        self.extract_links_button.setFixedHeight(40)  #
        self.extract_links_button.setStyleSheet("background-color: blue; color: white;margin-bottom:10px")
        self.extract_links_button.clicked.connect(self.start_link_extraction)
        layout.addWidget(self.extract_links_button)

        # Results display
        self.links_result = QTextEdit()
        layout.addWidget(QLabel("Extracted Links:"))
        layout.addWidget(self.links_result)

        # Save links button
        self.save_links_button = QPushButton("Save Links")
        self.save_links_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;margin-bottom:10px")
        self.save_links_button.clicked.connect(self.save_links_to_file)
        layout.addWidget(self.save_links_button)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Link Extractor")

    def create_email_extractor_tab(self):
        """Tab for extracting emails from URLs"""
        tab = QWidget()
        layout = QVBoxLayout()
          # Set spacing and margins for the main layout
        layout.setSpacing(2)  # Set minimal spacing between widgets
        layout.setContentsMargins(10, 10, 10, 10)  # Set margins (left, top, right, bottom)

        self.url_file_input = QLineEdit()
        self.url_file_input.setFixedHeight(40)  
        self.url_file_input.setPlaceholderText("Enter filename containing URLs (e.g., urls.txt)")
        layout.addWidget(QLabel("URL List File:"))
        layout.addWidget(self.url_file_input)

        self.extract_emails_button = QPushButton("Extract Emails")
        self.extract_emails_button.setFixedHeight(40)  
        self.extract_emails_button.setStyleSheet("background-color: blue; color: white;margin-bottom:10px")
        self.extract_emails_button.clicked.connect(self.start_email_extraction)
        layout.addWidget(self.extract_emails_button)

        # Results display for extracted emails
        self.emails_result = QTextEdit()
        layout.addWidget(QLabel("Extracted Emails:"))
        layout.addWidget(self.emails_result)

        # Save Email button
        self.save_email_button = QPushButton("Save Email")
        self.save_email_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;margin-bottom:10px")
        self.save_email_button.clicked.connect(self.save_email_to_file)
        layout.addWidget(self.save_email_button)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Email Extractor")

    def create_email_sender_tab(self):
        """Tab for sending emails"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Set spacing and margins for the main layout
        layout.setSpacing(2)  # Set minimal spacing between widgets
        layout.setContentsMargins(10, 10, 10, 10)  # Set margins (left, top, right, bottom)

        # Function to create label and input pair
        def add_label_input_pair(label_text, input_field):
            label = QLabel(label_text)
            label.setContentsMargins(0, 0, 0, 0)  # Set label margins to zero
            layout.addWidget(label)
            layout.addWidget(input_field)

        # Sender email input
        self.sender_email_input = QLineEdit()
        self.sender_email_input.setPlaceholderText("Enter your email")
        self.sender_email_input.setFixedHeight(40)  # Set fixed height for the input field
        add_label_input_pair("Sender Email:", self.sender_email_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your email password")
        self.password_input.setFixedHeight(40)  # Set fixed height for the input field
        add_label_input_pair("Password:", self.password_input)

        # Email list file input
        self.email_file_input = QLineEdit()
        self.email_file_input.setPlaceholderText("Enter path to email list file")
        self.email_file_input.setFixedHeight(40)  # Set fixed height for the input field
        add_label_input_pair("Email List File:", self.email_file_input)

        # Attachment input
        self.attachment_input = QLineEdit(self)
        self.attachment_input.setPlaceholderText("Select your CV file...")
        self.attachment_input.setFixedHeight(40)  # Set fixed height for the input field
        add_label_input_pair("Attachment:", self.attachment_input)

        # Button to browse for attachment
        self.attach_file_button = QPushButton("Browse", self)
        self.attach_file_button.setFixedHeight(40)  
        self.attach_file_button.setStyleSheet("background-color: blue; color: white;margin-bottom:10px")
        self.attach_file_button.clicked.connect(self.browse_file)
        layout.addWidget(self.attach_file_button)

        # Text area for logging output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.log_output)

        # Button to send emails
        self.send_emails_button = QPushButton("Send Emails")
        self.send_emails_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;margin-bottom:10px")
        self.send_emails_button.clicked.connect(self.start_email_sending)  # Connect to send_emails method
        layout.addWidget(self.send_emails_button)

     

        # Set layout for the tab
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Email Sender")
    # ======================== end tab =======================
    # =========================start link extract =====================
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
    # ==================end link extract======================
    # =====================start  email extract =======================
    def start_email_extraction(self):
        """Start the email extraction process in a separate thread"""
        filename = self.url_file_input.text()
        
        if filename:
            self.thread = QThread()
            self.thread.started.connect(lambda: self.extract_emails_from_urls(filename))  # Start extraction
            self.thread.finished.connect(self.thread.deleteLater)  # Clean up thread
            self.thread.start()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a filename containing URLs.")
 
    def extract_emails_from_urls(self, filename):
        """Function to extract emails from the specified URLs file"""
        global extracted_emails  # Use the global variable to hold extracted emails

        try:
            with open(filename, 'r') as file:
                urls = list(set(file.read().splitlines()))
            logger_info.info(f"{len(urls)} unique URLs found.")
            
            with requests.Session() as session:
                url_cache = {}
                url_chunks = [urls[i::2] for i in range(2)]
                with ThreadPoolExecutor(max_workers=2) as executor:
                    executor.map(lambda chunk: process_urls(chunk, session, url_cache), url_chunks)

            # پس از اتمام استخراج، به روز رسانی UI
            self.update_email_results(extracted_emails)  # Update the UI with extracted emails
            logger_info.info(f"Extracted Emails: {extracted_emails}")

        except Exception as e:
            raise BaseException(f"Error is :{e}")

    def update_email_results(self, emails):
        """Update the email display area with the extracted emails."""
        if emails:
            self.emails_result.setPlainText("\n".join(emails))  # Update QTextEdit with extracted emails
        else:
            self.emails_result.setPlainText("No emails found.")  # Inform if no emails found

    def save_email_to_file(self):
        
        """Save extracted emails to a file with a custom name"""
        emails = self.emails_result.toPlainText()
        print("Emails to save:", emails)
        if not emails:
            QMessageBox.warning(self, "No Emails", "There are no emails to save.")
            return
        # Debugging: Print the emails to the console
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
    # ===========================end  extract email ==================
    # ======================== start email sending======================

    def browse_file(self):
        """Open a file dialog to select a file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_name:
            self.attachment_input.setText(file_name)  # Set the selected file path in the input

    def start_email_sending(self):
        """Start the email sending process in a separate thread"""
        sender_email = self.sender_email_input.text()
        password = self.password_input.text()
        email_file = self.email_file_input.text()
        attachment_path = self.attachment_input.text()  # Get the file path from QLineEdit
        attachment_path if attachment_path else None
        if sender_email and password and email_file:
       
            attachment_path = attachment_path if attachment_path else None
            threading.Thread(target=self.send_emails, args=(sender_email, password, email_file, attachment_path), daemon=False).start()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            
    def send_emails(self, sender_email, password, email_file, attachment_path):
        self.log_output.append("Starting to send emails...")
        """Function to send emails to extracted email addresses with attachment"""
        asyncio.run(self.send_emails_async(sender_email, password, email_file, attachment_path))
        
    async def send_emails_async(self, sender_email, password, email_file, attachment_path):
        """Asynchronous email sending with attachment"""
        try:
            email_list = await read_email_list(email_file)
            for receiver_email in email_list:
                await self.send_email_with_retry(receiver_email, sender_email, password, attachment_path)
                await asyncio.sleep(10)  # Delay of 10 seconds between each email to avoid rate limits
                
            self.log_signal.emit("Emails sent successfully!")
            QMessageBox.information(self, "Success", "Emails sent successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while sending emails: {e}")

    async def send_email_with_retry(self, receiver_email, sender_email, password, attachment_path=None, retries=3, delay=5):
        """Send email with retry mechanism"""
        for attempt in range(retries):
            try:
                await send_email(
                    receiver_email=receiver_email,
                    html_content=html_content,
                    sender_email=sender_email,
                    password=password,
                    attachment_path=attachment_path
                )
                self.log_signal.emit(f"Email sent successfully to {receiver_email}!")  
                break  # If successful, exit the retry loop
            except Exception as e:
                self.log_signal.emit(f"Failed to send email to {receiver_email}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)  # Wait before retrying
                else:
                    self.log_signal.emit(f"Giving up on sending email to {receiver_email} after {retries} attempts.")  # استفاده از سیگنال
    # ======================== end email sending =====================


if __name__ == "__main__":
    setup_logging()
    logger_info = logging.getLogger('info')
    logger_info.info("This is an info message.")
    app = QApplication(sys.argv)
    # print(f"Saving to: {SAVE_FILE_PATH}")  #
    window = EmailAutomationApp()
    window.show()
    sys.exit(app.exec())
