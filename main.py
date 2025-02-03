import os
import time
from icecream import ic
from dotenv import load_dotenv
from parce_list import parse_page
from send_to_telegram import telegram_sender
from sendler.send_message import send_any_message


# Загрузить переменные окружения из .env
load_dotenv()


def main():
    DEBUG = bool(os.getenv("DEBUG"))

    DELAY = 3600
    try:
        DELAY = int(os.getenv("DELAY"))
    except:
        pass

    ic(DELAY)
    ic(DEBUG)

    message = "Привет! Бот работает, сейчас посмотрю что там новенького в мире кино!"
    send_any_message(message)

    while True:
        parse_page()
        telegram_sender()
        if not DEBUG:
            time.sleep(DELAY)
        else:
            message = "Бот завершил работу!"
            send_any_message(message)
            break

if __name__ == '__main__':
    main()
