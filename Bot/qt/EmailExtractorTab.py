from PyQt6.QtWidgets import QWidget, QVBoxLayout, QInputDialog, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import pyqtSignal
import asyncio
import threading
import requests
from ..worker_signals import WorkerSignals
from ..utils import read_email_list, setup_driver, process_urls

class EmailExtractorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # self.worker_signals = WorkerSignals()
        # self.worker_signals.update_emails.connect(self.update_emails_display)
        # self.worker_signals.finished.connect(self.on_finished)

    def setup_ui(self):
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
        
        # Save emails button
        self.save_emails_button = QPushButton("Save Emails")
        self.save_emails_button.clicked.connect(self.save_emails_to_file)
        layout.addWidget(self.save_emails_button)

        self.setLayout(layout)

    def start_email_extraction(self):
        """Start the email extraction process in a separate thread"""
        filename = self.url_file_input.text()
        
        if filename:  # Check if the user provided a filename
            threading.Thread(target=self.extract_emails_from_urls, args=(filename,), daemon=True).start()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a filename containing URLs.")

    def extract_emails_from_urls(self, filename):
        """Function to extract emails from the specified URLs file"""
        asyncio.run(self.extract_emails_async(filename))

    async def extract_emails_async(self, filename):
        """Asynchronous email extraction from URLs"""
        try:
            # Read and deduplicate URLs
            with open(filename, 'r') as file:
                urls = list(set(file.read().splitlines()))

            # Create a shared session and cache for URLs
            with requests.Session() as session:
                url_cache = {}  # Define cache for URLs
                extracted_emails = await process_urls(urls, session, url_cache)

            # Emit the signal to update the emails display
            self.worker_signals.update_emails.emit("\n".join(extracted_emails))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while reading URLs: {e}")

        finally:
            self.worker_signals.finished.emit()  # Emit finished signal

    def update_emails_display(self, emails):
        """Update the emails display in the GUI."""
        self.emails_result.setPlainText(emails)

    def on_finished(self):
        """Handle the finish signal from the worker."""
        QMessageBox.information(self, "Finished", "Email extraction completed successfully!")

    def save_emails_to_file(self):
        """Save extracted emails to a file with a predefined name."""
        emails = self.emails_result.toPlainText()
        if not emails:
            QMessageBox.warning(self, "No Emails", "There are no emails to save.")
            return

        file_name, ok = QInputDialog.getText(self, "Input Dialog", "Enter the filename to save (e.g., emails.txt):")
        
        if ok and file_name:  # Check if the user clicked OK and provided a filename
            file_name = file_name.strip()  # Strip any whitespace
            if not file_name.endswith('.txt'):  # Ensure the file has a .txt extension
                file_name += '.txt'
            try:
                with open(file_name, "w") as file:
                    file.write(emails)
                QMessageBox.information(self, "Success", f"Emails saved successfully to {file_name}!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving the file: {e}")
