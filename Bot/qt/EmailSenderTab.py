from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import pyqtSignal
import threading
# from worker_signals import WorkerSignals
# from ..email_content import html_content, attachment_path
from ..email_sender import send_email,html_content, attachment_path
from ..utils import read_email_list

class EmailSenderTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # self.worker_signals = WorkerSignals()
        # self.worker_signals.finished.connect(self.on_finished)

    def setup_ui(self):
        layout = QVBoxLayout()

        # Email list input
        self.email_list_input = QLineEdit()
        self.email_list_input.setPlaceholderText("Enter filename containing email addresses (e.g., emails.txt)")
        layout.addWidget(QLabel("Email List File:"))
        layout.addWidget(self.email_list_input)

        # Subject and message input
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter email subject")
        layout.addWidget(QLabel("Subject:"))
        layout.addWidget(self.subject_input)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter email message")
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)

        # Send email button
        self.send_email_button = QPushButton("Send Email")
        self.send_email_button.clicked.connect(self.start_email_sending)
        layout.addWidget(self.send_email_button)

        self.setLayout(layout)

    def start_email_sending(self):
        """Start the email sending process in a separate thread"""
        email_list_file = self.email_list_input.text()
        subject = self.subject_input.text()
        message = self.message_input.toPlainText()

        if email_list_file and subject and message:
            threading.Thread(target=self.send_emails, args=(email_list_file, subject, message), daemon=True).start()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all the required fields.")


    def send_emails(self, email_list_file, subject, message):
        """Function to send emails to the specified email list"""
        try:
            email_list = read_email_list(email_list_file)
            for email in email_list:
                send_email(email, subject, html_content, attachment_path)
            self.worker_signals.finished.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while sending emails: {e}")

    def on_finished(self):
        """Handle the finish signal from the worker."""
        QMessageBox.information(self, "Finished", "Email sending completed successfully!")



