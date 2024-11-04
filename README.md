# Email Handler

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
  
You can install these libraries using pip:

```bash
python -m venv venv
source ./venv /bin/activate
cd Bot
python run_main.py
python run_getmail.py
python run_sender.py