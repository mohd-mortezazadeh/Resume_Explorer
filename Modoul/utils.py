# utils.py

import logging

logger_info = logging.getLogger('info')

def save_email(email_address):
    """Save the extracted email to a file."""
    with open('SaveEmail.txt', 'a') as email_file:
        email_file.write(email_address + '\n')
    print(f"Saved email: {email_address}")

def stop_program():
    """Stop the email extraction process."""
    global should_stop
    should_stop = True


# utils.py

def read_email_list(file_path):
    """Read email addresses from file and return them as a list."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f]
