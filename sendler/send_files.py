import requests
from icecream import ic
from logger import print_error


def send_torrent_file(bot_token, chat_id, file_name, caption=""):
    """Отправляет торрент-файл с описанием в Telegram."""
    send_document_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_name, "rb") as torrent_file:
        try:
            response = requests.post(
                send_document_url,
                data={
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": "HTML"  # Опционально, для форматирования описания
                },
                files={"document": torrent_file}
            )
            if response.status_code == 200:
                # ic("Torrent file sent successfully.")
                pass
            else:
                print_error(f"[send_torrent_file] Error sending torrent file: {response.status_code} - {response.text}")
        except Exception as e:
            print_error(f"[send_torrent_file] Error sending torrent file:", e)
