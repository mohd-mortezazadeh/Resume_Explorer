import logging
from datetime import datetime

def setup_logging(log_file=None):
    """Set up logging configuration."""
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG to capture all types of log messages

    # If no log_file is provided, create a dynamic log file name based on current date and time
    if log_file is None:
        log_file = f'Log/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Create handlers
    console_handler = logging.StreamHandler()  # Log to console
    file_handler = logging.FileHandler(log_file)  # Log to file

    # Set level for handlers
    console_handler.setLevel(logging.INFO)  # Set console log level to INFO
    file_handler.setLevel(logging.DEBUG)  # Set file log level to DEBUG

    # Create formatters and add them to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
