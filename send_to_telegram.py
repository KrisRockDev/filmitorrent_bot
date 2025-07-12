import os
import requests
from dotenv import load_dotenv
import os
import requests
import json  # Added for handling posted_messages.json
from icecream import ic
from settings import base_dir_absolute, users_dir_absolute, POSTED_MESSAGES_DB  # Added POSTED_MESSAGES_DB
from sendler.send_images import send_poster_with_info, send_stills_with_description_as_reply  # Updated imports
from sendler.send_files import send_torrent_file
from dotenv import load_dotenv

# Загрузить переменные окружения из .env
load_dotenv()

CHANNEL_ID = os.getenv('CHANNEL_ID')

# Токен бота
BOT_TOKEN = os.getenv("TOKEN")


# CHAT_ID is no longer the primary target for posts, CHANNEL_ID will be used.
# CHAT_ID = os.getenv("CHAT_ID") # Commented out or remove if not used elsewhere for admin notifications etc.

# ic(BOT_TOKEN)

# Helper functions for managing posted messages JSON database
def load_posted_messages():
    """Loads posted messages data from POSTED_MESSAGES_DB."""
    if os.path.exists(POSTED_MESSAGES_DB):
        try:
            with open(POSTED_MESSAGES_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            ic(f"Error loading {POSTED_MESSAGES_DB}: {e}")
            return {}
    return {}


def save_posted_messages(data):
    """Saves data to POSTED_MESSAGES_DB as JSON."""
    try:
        with open(POSTED_MESSAGES_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        ic(f"Error saving to {POSTED_MESSAGES_DB}: {e}")


def film_path():
    list_dir = os.listdir(base_dir_absolute)
    if list_dir:
        return list_dir
    else:
        return False


def get_film_items(film_dir):
    list_dir = os.listdir(film_dir)
    if 'new' in list_dir:
        return list_dir
    else:
        return False


def del_new(film_dir):
    list_dir = os.listdir(film_dir)
    if 'new' in list_dir:
        new_file = os.path.join(film_dir, 'new')
        os.remove(new_file)


def torrent_file_info(file_name):
    q_list = {
        'WEB-DLRip': '🟡 WEB-DLRip',
        'WEB-DLRip-AVC': '🟡 WEB-DLRip-AVC',
        '720p': '🟡 720p',
        '1080p': '🟢 1080p',
        '2160p': '🔴 2160p',
    }
    res = '🟡 WEB-DL'
    for i in q_list:
        if i in file_name:
            res = q_list[i]
    return f"{res}  📥 Размер: {file_name.split('size.')[-1].split('.torrent')[0]}"


def send_to_channel(film_dir, lst):  # Renamed function, CHAT_ID is now CHANNEL_ID
    """Sends movie information, stills, and torrents to the designated Telegram channel."""
    if not BOT_TOKEN:
        ic("BOT_TOKEN не найден. Проверьте .env файл.")
        return
    if not CHANNEL_ID:
        ic("CHANNEL_ID не найден. Проверьте settings.py и .env файл.")
        return

    film_name_identifier = os.path.basename(film_dir)
    info_file_path = os.path.join(film_dir, 'info.txt')

    # 1. Send Poster (Main Post)
    ic(f"Отправка постера для фильма: {film_name_identifier} в канал {CHANNEL_ID}")
    message_id = send_poster_with_info(
        bot_token=BOT_TOKEN,
        chat_id=CHANNEL_ID,
        info_file_path=info_file_path,
        image_folder=film_dir
    )

    if not message_id:
        ic(f"Ошибка отправки постера для {film_name_identifier}. Пропуск дальнейшей отправки.")
        return

    ic(f"Постер для {film_name_identifier} успешно отправлен. Message ID: {message_id}")

    posted_messages = load_posted_messages()
    if film_name_identifier not in posted_messages:
        posted_messages[film_name_identifier] = {}

    posted_messages[film_name_identifier]['message_id'] = message_id
    posted_messages[film_name_identifier].setdefault('sent_torrents', [])  # Initialize if not present

    # 2. Prepare and Send Stills (as Reply)
    all_jpgs = sorted([item for item in lst if item.lower().endswith('.jpg') and item.lower() != 'poster.jpg'])
    stills_to_send = all_jpgs[:3]

    if stills_to_send:  # Check if there are any stills to send
        ic(f"Подготовка к отправке {len(stills_to_send)} кадров для {film_name_identifier}")
        if len(stills_to_send) < 3:
            ic(f"Внимание: Найдено только {len(stills_to_send)} кадров вместо 3 для {film_name_identifier}.")

        send_stills_with_description_as_reply(
            bot_token=BOT_TOKEN,
            chat_id=CHANNEL_ID,
            reply_to_message_id=message_id,
            info_file_path=info_file_path,
            image_folder=film_dir,
            stills_images_list=stills_to_send
        )
        ic(f"Кадры для {film_name_identifier} отправлены.")
    else:
        ic(f"Кадры для {film_name_identifier} не найдены или не выбраны.")

    # 3. Send Torrent Files (as Replies)
    sent_torrents_for_this_movie = posted_messages[film_name_identifier].get('sent_torrents', [])

    for item in lst:
        if '.torrent' in item:
            if item not in sent_torrents_for_this_movie:  # Check if torrent was already sent
                ic(f"Отправка торрент-файла: {item} для {film_name_identifier}")
                send_torrent_file(
                    bot_token=BOT_TOKEN,
                    chat_id=CHANNEL_ID,
                    file_name=os.path.join(film_dir, item),
                    caption=torrent_file_info(item),
                    reply_to_message_id=message_id
                )
                sent_torrents_for_this_movie.append(item)
            else:
                ic(f"Торрент-файл {item} уже был отправлен для {film_name_identifier}, пропуск.")

    posted_messages[film_name_identifier]['sent_torrents'] = sent_torrents_for_this_movie
    save_posted_messages(posted_messages)
    ic(f"Информация о посте для {film_name_identifier} сохранена в {POSTED_MESSAGES_DB}")


def telegram_sender():
    """
    Main function to find new films and send them to the Telegram channel.
    Marks films as processed using the 'new' file mechanism.
    """
    if not BOT_TOKEN:  # Added check for BOT_TOKEN
        ic("BOT_TOKEN не найден в .env. Отправка невозможна.")
        return
    if not CHANNEL_ID:  # Added check for CHANNEL_ID
        ic("CHANNEL_ID не определен. Отправка невозможна.")
        return

    if list_dir := film_path():
        for film_folder_name in list_dir:
            film_dir_path = os.path.join(base_dir_absolute, film_folder_name)
            if lst_of_files := get_film_items(film_dir_path):  # Checks for 'new' file
                ic(f"Найден новый фильм: {film_folder_name}")
                # ic(film_dir_path)
                # ic(lst_of_files)
                send_to_channel(film_dir_path, lst_of_files)  # Changed to send_to_channel
                del_new(film_dir_path)  # Maintain this to mark as processed for initial send
                ic(f"Обработка фильма {film_folder_name} завершена, 'new' файл удален.")
            # else: # Optional: log if a folder doesn't have a 'new' file
            # ic(f"Папка {film_folder_name} не содержит 'new' файла, пропуск.")
    # else: # Optional: log if no film folders found
    # ic("Не найдено папок с фильмами в base_dir_absolute.")


if __name__ == "__main__":
    ic("Запуск telegram_sender...")
    telegram_sender()
    ic("telegram_sender завершил работу.")
