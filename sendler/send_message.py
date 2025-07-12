import requests
from icecream import ic
import os
from dotenv import load_dotenv
from logger import print_error


def send_any_message(message):
    load_dotenv()

    # Замените на ваш токен бота и chat_id
    bot_token = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    USERS = [CHAT_ID, ]
    if ',' in CHAT_ID:
        USERS = CHAT_ID.replace(' ', '').split(',')

    # ic(USERS)
    for chat_id in USERS:
        """Отправляет приветственное сообщение в Telegram."""
        send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            response = requests.post(
                send_message_url,
                data={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"  # Опционально, для форматирования текста
                }
            )
            if response.status_code == 200:
                # ic("Welcome message sent successfully.")
                pass
            else:
                print(f"[send_welcome_message] Error sending message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[send_welcome_message] Error sending message:", e)


def send_text_message_as_reply(bot_token, chat_id, text, reply_to_message_id):
    """Отправляет текстовое сообщение в ответ на другое сообщение в Telegram."""
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_to_message_id": reply_to_message_id,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(send_message_url, data=data)
        if response.status_code == 200:
            # ic("Reply message sent successfully.")
            return True
        else:
            print_error(
                f"[send_text_message_as_reply] Error sending reply message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"[send_text_message_as_reply] Error sending reply message: {e}")
        return False
