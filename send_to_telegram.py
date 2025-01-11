import os
import requests
from dotenv import load_dotenv
from icecream import ic
from settings import *
from sendler.send_images import send_photos_with_captions
from sendler.send_files import send_torrent_file

# Загрузить переменные окружения из .env
load_dotenv()

# Замените на ваш токен бота и chat_id
BOT_TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ic(BOT_TOKEN)
# ic(CHAT_ID)

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
        'WEB-DLRip-AVC':'🟡 WEB-DLRip-AVC',
        '720p':'🟡 720p',
        '1080p':'🟢 1080p',
        '2160p':'🔴 2160p',
    }
    res = '🟡 WEB-DL'
    for i in q_list:
        if i in file_name:
            res = q_list[i]
    return f"{res}  📥 Размер: {file_name.split('size.')[-1].split('.torrent')[0]}"


def send_to_users(film_dir, lst):
    users = ''
    if os.path.isfile(users_dir_absolute):
        with open(file=users_dir_absolute, mode='r', encoding='utf8') as f:
            users = f.read()
            if '\n' in users:
                users = users.strip().split('\n')

    users_list = []
    for u in users:
        if u != '':
            users_list.append(u)

    USERS = [CHAT_ID, ] + users_list
    if ',' in CHAT_ID:
        USERS = CHAT_ID.replace(' ', '').split(',')

    # Отправка фото и файл с описанием
    USERS = list(set(USERS))
    # ic(USERS)
    for USER in USERS:
        img_list = []
        for item in lst:
            if '.jpg' in item:
                img_list.append(item)

        send_photos_with_captions(
            bot_token=BOT_TOKEN,
            chat_id=USER,
            info_file_path=os.path.join(film_dir, 'info.txt'),
            image_folder=film_dir,
            images_list=img_list[::-1]
        )

        for item in lst:
            if '.torrent' in item:
                send_torrent_file(
                    bot_token=BOT_TOKEN,
                    chat_id=CHAT_ID,
                    file_name=os.path.join(film_dir, item),
                    caption=torrent_file_info(item)
                )


def telegram_sender():
    if list_dir := film_path():
        for film in list_dir:
            film_dir = os.path.join(base_dir_absolute, film)
            if lst := get_film_items(film_dir):
                # ic(film_dir)
                # ic(lst)
                send_to_users(film_dir, lst)
                del_new(film_dir)


if __name__ == "__main__":
    telegram_sender()
