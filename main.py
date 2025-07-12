import os
import time
from icecream import ic
from dotenv import load_dotenv
from parce_list import parse_page
from send_to_telegram import telegram_sender
from sendler.send_message import send_any_message
from torrent_updater import run_torrent_update_check # Added import

# Загрузить переменные окружения из .env
load_dotenv()
CHANNEL_ID = os.getenv('CHANNEL_ID')

def main():
    # Check for CHANNEL_ID early
    if not CHANNEL_ID:
        ic("CRITICAL: CHANNEL_ID is not set in .env or settings.py. Bot notifications and primary functions may fail.")
        print("CRITICAL: CHANNEL_ID is not set. Please set it in your .env file or settings.py.")
        # Depending on desired behavior, you might want to exit here if CHANNEL_ID is crucial for all operations
        # return

    DEBUG = bool(os.getenv("DEBUG"))

    DELAY = 3600
    try:
        DELAY = int(os.getenv("DELAY"))
    except (TypeError, ValueError): # More specific exception handling
        ic(f"Invalid DELAY value: {os.getenv('DELAY')}. Using default: {DELAY}")
        pass

    ic(DELAY)
    ic(DEBUG)

    # Message now goes to CHAT_ID (admin/debug) or CHANNEL_ID if they are the same
    start_message = "Бот запускается... Проверка новых фильмов и обновлений торрентов."
    ic(start_message)
    send_any_message(start_message)

    while True:
        ic("Запуск цикла парсинга и отправки...")
        try:
            parse_page()
            telegram_sender()
        except Exception as e:
            ic(f"Ошибка во время parse_page() или telegram_sender(): {e}")
            send_any_message(f"Произошла ошибка при парсинге или отправке новых фильмов: {e}")


        ic("Запуск проверки обновлений торрентов...")
        try:
            run_torrent_update_check()
        except Exception as e:
            ic(f"Ошибка во время run_torrent_update_check(): {e}")
            send_any_message(f"Произошла ошибка при проверке обновлений торрентов: {e}")

        if not DEBUG:
            ic(f"Работа завершена, ожидание {DELAY} секунд...")
            time.sleep(DELAY)
        else:
            finish_message = "Бот завершил работу в режиме DEBUG."
            ic(finish_message)
            send_any_message(finish_message)
            break

if __name__ == '__main__':
    main()
