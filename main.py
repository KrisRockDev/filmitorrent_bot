import os
import time
import datetime
import requests
from icecream import ic
from bs4 import BeautifulSoup
from settings import filmitorrent, films_list_base, DEBUG
from dotenv import load_dotenv

from send_to_telegram import telegram_sender
from parce_list import parse_page


# Загрузить переменные окружения из .env
load_dotenv()


def main():
    DELAY = 3600
    try:
        DELAY = int(os.getenv("DELAY"))
    except:
        pass

    ic(DELAY)
    ic(DEBUG)

    while True:
        parse_page()
        telegram_sender()
        if not DEBUG:
            time.sleep(DELAY)
        else:
            break

if __name__ == '__main__':
    main()
