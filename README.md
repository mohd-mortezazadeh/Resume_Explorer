# ResumeRover

Email Handler is a simple and efficient tool for managing and sending emails using Python. This project allows you to automate the sending of emails and easily work with a list of email addresses.

## Features

- Send HTML emails with content and attachments
- Read email lists from a file
- Log informational messages and errors
- Simple and user-friendly design

## Prerequisites

To use this project, you need the following:

- Python 3.6 or higher
- The following libraries:
  - `aiofiles`
  - `smtplib`
  - `ssl`
  - `email`
  


  

```bash
git clone https://github.com/pydevcasts/Email_Handler.git
cd Email_Handler
python -m venv venv
source ./venv /bin/activate
#You can install the libraries using pip:
pip install -r ./requirements.txt
cd Bot
python run_main.py
python run_getmail.py
python run_sender.py

## Project Structure
Email_Handler/
└── ‌Bot  
        ├── email_sender.py        # Main file for sending emails
        ├── utils.py               # Helper functions for managing emails
        ├── email_content.py       # Content and settings for emails
        ├── run_main.py            # Entry point of the program
        ├── run_sender.py          # Script for sending emails
        └── run_getmail.py         # Script for retrieving emails