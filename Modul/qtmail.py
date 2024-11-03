import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
from link_extractor import fetch_links  # فرض بر این است که این تابع را در ماژول link_extractor ایجاد کرده‌اید.
from email_extractor import fetch_emails  # فرض بر این است که این تابع را در ماژول email_extractor ایجاد کرده‌اید.
from email_sender import send_email  # فرض بر این است که این تابع را در ماژول email_sender ایجاد کرده‌اید.

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui.ui', self)  # بارگذاری فایل .ui طراحی شده
        self.extract_links_button.clicked.connect(self.extract_links)
        self.extract_emails_button.clicked.connect(self.extract_emails)
        self.send_email_button.clicked.connect(self.send_email)

    def extract_links(self):
        query = self.search_input.text()
        links = process_links(query)  # به فرض وجود تابع fetch_links
        self.links_output.setPlainText('\n'.join(links))
        QMessageBox.information(self, "Links Extracted", f"Found {len(links)} links.")

    def extract_emails(self):
        urls = self.links_output.toPlainText().splitlines()
        emails = fetch_emails(urls)  # به فرض وجود تابع fetch_emails
        self.emails_output.setPlainText('\n'.join(emails))
        QMessageBox.information(self, "Emails Extracted", f"Found {len(emails)} emails.")

    def send_email(self):
        email_content = self.email_content.toPlainText()
        recipient = self.recipient_input.text()
        send_email(recipient, email_content)  # به فرض وجود تابع send_email
        QMessageBox.information(self, "Email Sent", f"Email sent to {recipient}.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
