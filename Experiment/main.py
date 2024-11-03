# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox, QTabWidget, QFileDialog
from Experiment.web_scraper import ScraperThread
from Experiment.email_extractor import start_email_extraction
# from email_sender import send_email

class WebScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.scraper_thread = None

    def init_email_extraction_tab(self):
        """Initialize the Email Extraction tab."""
        layout = QVBoxLayout()  # Create a vertical layout for the tab

        self.email_input = QTextEdit(self)  # Create a text area for user input
        self.email_input.setPlaceholderText("Enter text or URL to extract emails")
        layout.addWidget(self.email_input)  # Add the text area to the layout

        self.extract_button = QPushButton("Extract Emails", self)  # Create a button
        self.extract_button.clicked.connect(self.extract_emails)  # Connect button click to a method
        layout.addWidget(self.extract_button)  # Add the button to the layout

        self.extracted_emails_area = QTextEdit(self)  # Create another text area for displaying extracted emails
        self.extracted_emails_area.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.extracted_emails_area)  # Add it to the layout

        self.email_extraction_tab.setLayout(layout)  # Set the layout for the tab

    def init_ui(self):
        self.setWindowTitle("Multi-functional App")
        self.setGeometry(100, 100, 600, 400)

        # Tab widget
        self.tabs = QTabWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tabs)

        # Web Scraping Tab
        self.scraping_tab = QWidget()
        self.tabs.addTab(self.scraping_tab, "Web Scraping")
        self.init_scraping_tab()

        # Email Extraction Tab
        self.email_extraction_tab = QWidget()
        self.tabs.addTab(self.email_extraction_tab, "Email Extraction")
        self.init_email_extraction_tab()

        # Email Sending Tab
        self.email_sending_tab = QWidget()
        self.tabs.addTab(self.email_sending_tab, "Send Email")
        # self.init_email_sending_tab()
    def init_email_extraction_tab(self):
        """Initialize the Email Extraction tab."""
        layout = QVBoxLayout()  # Create a vertical layout for the tab

        # Text area for user input (URL file)
        self.url_input = QLineEdit(self)  # Change to QLineEdit
        self.url_input.setPlaceholderText("Enter the path to the URL file")
        layout.addWidget(self.url_input)  # Add the text area to the layout

        # Text area for output file path
        self.output_input = QLineEdit(self)  # Change to QLineEdit
        self.output_input.setPlaceholderText("Enter the path to save the extracted emails")
        layout.addWidget(self.output_input)  # Add the text area to the layout
        self.results_area = QTextEdit(self)
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)
        # Button to trigger email extraction
        self.extract_button = QPushButton("Extract Emails", self)
        self.extract_button.clicked.connect(self.extract_emails)  # Connect button click to the extraction method
        layout.addWidget(self.extract_button)  # Add the button to the layout

        # Button to delete the output file
        self.delete_button = QPushButton("Delete Output File", self)
        self.delete_button.clicked.connect(self.delete_output_file)  # Connect to the delete method
        layout.addWidget(self.delete_button)  # Add the delete button to the layout
    # Logging area
        # self.log_area = QTextEdit(self)  # Create a QTextEdit for logs
        # self.log_area.setReadOnly(True)  # Make it read-only
        # layout.addWidget(self.log_area)  # Add the log area to the layout

        # Set the layout for the email extraction tab
        self.email_extraction_tab.setLayout(layout)

    def extract_emails(self):
        """Extract emails from the input text or URL."""
        url_file = self.url_input.text().strip()  # Get the URL file path
        output_file = self.output_input.text().strip()  # Get the output file path
        
        if url_file and output_file:  # Ensure both fields are filled
            # self.log_area.append(f"Starting extraction from: {url_file} to {output_file}")
            start_email_extraction(url_file, output_file)  # Call the extraction function
            # self.log_area.append("Extraction completed.")
        else:
            QMessageBox.warning(self, "Input Error", "Please provide both URL file and output file paths.")


    def delete_output_file(self):
        """Delete the specified output file."""
        output_file = self.output_input.text().strip()  # Get the output file path
        if output_file and os.path.exists(output_file):
            os.remove(output_file)  # Delete the file
            QMessageBox.information(self, "Success", f"Deleted file: {output_file}")
        else:
            QMessageBox.warning(self, "Error", "File not found or no file specified.")

    def init_scraping_tab(self):
        layout = QVBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter your search query")
        layout.addWidget(self.search_input)

        self.filename_input = QLineEdit(self)
        self.filename_input.setPlaceholderText("Enter filename to save (without extension)")
        layout.addWidget(self.filename_input)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        self.results_area = QTextEdit(self)
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)

        self.delete_button = QPushButton("Delete Saved File", self)
        self.delete_button.clicked.connect(self.delete_file)
        self.delete_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.delete_button)

        self.scraping_tab.setLayout(layout)

    def start_search(self):
        search_query = self.search_input.text()
        filename = self.filename_input.text().strip() + ".txt"  # Add .txt extension
        if not search_query:
            QMessageBox.warning(self, "Input Error", "Please enter a search query.")
            return
        if not filename or filename == ".txt":
            QMessageBox.warning(self, "Input Error", "Please enter a valid filename.")
            return
        
        self.results_area.clear()
        self.scraper_thread = ScraperThread(search_query, filename)
        self.scraper_thread.update_results.connect(self.append_results)
        self.scraper_thread.finished_scraping.connect(self.save_links_to_file)
        self.scraper_thread.finished_scraping.connect(self.show_completion_message)
        self.scraper_thread.start()

    def append_results(self, results):
        self.results_area.append(results)

    def save_links_to_file(self, links, filename):
        """Save the valid links to a file."""
        with open(filename, "w") as file:
            for link in links:
                file.write(link + "\n")
        QMessageBox.information(self, "Success", f"Valid URLs saved to {filename}")
        self.delete_button.setEnabled(True)  # Enable delete button

    def show_completion_message(self, links, filename):
        """Show a message when scraping is completed."""
        QMessageBox.information(self, "Completed", "URL extraction completed successfully!")

    def delete_file(self):
        filename = self.filename_input.text().strip() + ".txt"  # Get the filename
        if os.path.exists(filename):
            os.remove(filename)
            QMessageBox.information(self, "Deleted", f"{filename} has been deleted.")
            self.delete_button.setEnabled(False)  # Disable delete button again
        else:
            QMessageBox.warning(self, "Error", f"{filename} does not exist.")

    # (Other methods for email extraction and sending...)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebScraperApp()
    window.show()
    sys.exit(app.exec())