from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QInputDialog,QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import pyqtSignal
import asyncio
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from ..worker_signals import WorkerSignals

from ..link_extractor import process_links,validate_links
from ..driver_setup import setup_driver
class LinkExtractorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # self.worker_signals = WorkerSignals()
        # self.worker_signals.update_links.connect(self.update_links_display)
        # self.worker_signals.finished.connect(self.on_finished)

    def setup_ui(self):
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

        self.setLayout(layout)

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
            input_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "q"))
            )
            input_element.send_keys(search_query)
            input_element.submit()

            links = set()  # To store unique valid links
            page_num = 1   # Track page number

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)

                current_links = process_links(driver)
                valid_links = await validate_links(current_links)
                links.update(valid_links)

                await asyncio.sleep(1)

                try:
                    element = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, 'pnnext'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    element.click()
                    await asyncio.sleep(1)
                    page_num += 1

                except Exception:
                    break

            # Emit the signal to update the links display
            self.worker_signals.update_links.emit("\n".join(links))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        finally:
            driver.quit()
            self.worker_signals.finished.emit()  # Emit finished signal

    def update_links_display(self, links):
        """Update the links display in the GUI."""
        self.links_result.setPlainText(links)

    def on_finished(self):
        """Handle the finish signal from the worker."""
        QMessageBox.information(self, "Finished", "Link extraction completed successfully!")

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
