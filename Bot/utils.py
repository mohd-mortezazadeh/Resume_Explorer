# utils.py

import logging
import os
import aiofiles


# Create a logger instance
logger_info = logging.getLogger(__name__)

def save_email(email_address, file_name):
    """Save the extracted email to a file."""
    try:
        with open(file_name, 'a') as email_file:
            email_file.write(email_address + '\n')
        logger_info.info(f"Saved email: {email_address}")
    except Exception as e:
        logger_info.error(f"Error saving email {email_address}: {e}")
        
        
def stop_program():
    """Stop the email extraction process."""
    global should_stop
    should_stop = True
    

async def read_email_list(file_path):
    """Read email addresses from file and return them as a list."""
    if not os.path.exists(file_path):
        logger_info.error(f"File not found: {file_path}")
        return []

    try:
        async with aiofiles.open(file_path, mode='r') as f:
            return [line.strip() for line in await f.readlines()]
    except Exception as e:
        logger_info.error(f"Error reading file {file_path}: {e}")
        return []



