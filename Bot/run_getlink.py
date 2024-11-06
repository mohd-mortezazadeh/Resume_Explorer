# main.py

import asyncio
from utils import scroll_and_load_nav_shared
from conf_log import setup_logging



async def main(file_name):
    await scroll_and_load_nav_shared(file_name)

    
if __name__ == "__main__":
    setup_logging()
    filename = input("what is your file name to save: ")
    asyncio.run(main(filename))  # Use asyncio.run to execute the main coroutine