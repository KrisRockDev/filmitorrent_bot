import os
import requests
from dotenv import load_dotenv
from icecream import ic
from settings import *

# Загрузить переменные окружения из .env
load_dotenv()

# Замените на ваш токен бота и chat_id
BOT_TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ic(BOT_TOKEN)
# ic(CHAT_ID)


# Данные фильма
data_dict = {
    'poster': 'http://filmitorrent.net/uploads/posts/2024-12/thumbs/1735547056_9082b1712a.jpg',
    'torrent_file': 'http://filmitorrent.net/torrenti/7/14/Odin.den.v.Stambule.2024.WEB-DL.1080p_54493_93.torrent',
    'url:': 'https://filmitorrent.net/komedia/5449-odin-den-v-stambule-2024.html',
    'Актеры:': 'Леонид Барац, Камиль Ларин, Ростислав Хаит, Александр Демидов, '
               'Тарас Кузьмин, Арина Маракулина, Анастасия Белоусова',
    'Время:': '1 ч 24 мин',
    'Год:': '2024',
    'Жанр:': 'комедия',
    'Название:': 'Один день в Стамбуле',
    'Опубликовано:': '30-12-2024, 11:24',
    'Режиссер:': 'Авет Оганесян',
    'Рейтинг:': '6.3',
    'Страна:': 'Россия'
}


def build_message(data):
    """Собирает текст сообщения из словаря данных."""
    cat_list = [
        'Название:',
        'Год:',
        'Время:',
        'Страна:',
        'Рейтинг:',
        'Режиссер:',
        'Актеры:',
        'Жанр:',
        'url:',
        'Опубликовано:',
    ]

    for cat_item in cat_list:
        if cat_item not in data:
            data[cat_item] = '---'

    return (
        f"🎬 <b>{data['Название:']}</b>\n"
        f"📅 Год: {data['Год:']}\n"
        f"⏳ Время: {data['Время:']}\n"
        f"🌍 Страна: {data['Страна:']}\n"
        f"⭐️ Рейтинг: {data['Рейтинг:']}\n"
        f"🎥 Режиссер: {data['Режиссер:']}\n"
        f"🤡 Актеры: {data['Актеры:']}\n"
        f"🎭 Жанр: {data['Жанр:']}\n"
        f"🗓 Дата публикации: {data['Опубликовано:']}\n"
        f"🔗 <a href='{data['url:']}'>Подробнее</a>\n"
    )


def download_file(url, save_path):
    """Скачивает файл по ссылке."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return save_path
    except Exception as e:
        ic(f"Error downloading file from {url}: {e}")
        return None


def send_photo_with_caption(bot_token, chat_id, message, poster_url):
    """Отправляет сообщение с текстом и постером в Telegram."""
    send_photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    # Скачиваем постер
    poster_path = download_file(poster_url, "poster.jpg")
    if poster_path:
        with open(poster_path, "rb") as poster_file:
            try:
                response = requests.post(
                    send_photo_url,
                    data={
                        "chat_id": chat_id,
                        "caption": message,
                        "parse_mode": "HTML"
                    },
                    files={"photo": poster_file}
                )
                # ic("Photo response:", response.status_code, response.text)
            except Exception as e:
                ic("Error sending photo and caption:", e)
        os.remove(poster_path)  # Удаляем файл после отправки
    else:
        ic("Постер не найден или не скачан.")


def send_torrent_file(bot_token, chat_id, torrent_url, file_name):
    """Отправляет торрент-файл в Telegram."""
    send_document_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    for _ in range(10):
        rep_list = [
            '?', '/', r'\\'[-1], ':', '*', '"', '<', '>', '|', ' ', '__', '_ ', ' _',
        ]

        for simbol in rep_list:
            file_name = file_name.replace(simbol, '_')

    # Скачиваем торрент-файл
    torrent_path = download_file(torrent_url, f"{file_name}.torrent")
    if torrent_path:
        with open(torrent_path, "rb") as torrent_file:
            try:
                response = requests.post(
                    send_document_url,
                    data={
                        "chat_id": chat_id,
                    },
                    files={"document": torrent_file}
                )
                # ic("Torrent response:", response.status_code, response.text)
            except Exception as e:
                ic("Error sending torrent file:", e)
        os.remove(torrent_path)  # Удаляем файл после отправки
    else:
        ic("Торрент-файл не найден или не скачан.")


def telegram_sender(data_dict):
    # Построение сообщения
    message = build_message(data_dict)

    # Ссылки на постер и торрент
    poster_url = data_dict['poster']
    torrent_url = data_dict['torrent_file']

    if not os.path.exists(users_file):
        with open(file=users_file, mode='w', encoding='utf8') as f:
            f.write('')

    with open(file=users_file, mode='r', encoding='utf8') as f:
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
    for USER in list(set(USERS)):
        send_photo_with_caption(BOT_TOKEN, USER, message, poster_url)
        send_torrent_file(BOT_TOKEN, USER, torrent_url, data_dict['Название:'])
        print(
            f"Пользователю {USER} отправлено сообщение о фильме {data_dict['Название:']}")  # ic(f"Сообщение отправлено пользователю {USER}")


if __name__ == "__main__":
    telegram_sender(data_dict)
