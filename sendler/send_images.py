import os
import requests
import json
from icecream import ic
from logger import print_error


def parse_info_file(file_path):
    """Читает текстовый файл и преобразует его в словарь."""
    data = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                data[key.strip()] = value.strip()

    with open(os.path.join(os.path.split(file_path)[0], 'des.txt'), mode='r', encoding='utf-8') as f:
        data['Описание'] = f.read()
    return data


def build_message_without_description(data):
    """Собирает текст сообщения из словаря данных без описания."""
    fields = {
        'Название': "🎬 <b>{}</b>",
        'Оригинальное название': "©️ {}",
        'Слоган': "🗣 Слоган: {}",
        'Жанр': "🎭 Жанр: {}",
        'Год': "🗓 Год: {}",
        'Продолжительность': "⏱ Продолжительность: {}",
        'Страна': "🌍 Страна: {}",
        'Рейтинг': "⭐ Рейтинг: {}",
        'Режиссер': "🎥 Режиссер: {}",
        'Актеры': "🤡 Актеры: {}",
        'Премьера в мире': "🌐 Премьера в мире: {}",
        'Дата выхода в России': "🇷🇺 Дата выхода в России: {}"
    }

    message_parts = [fields[key].format(data[key]) for key in fields if
                     key in data and data[key] and data[key] != '---']

    if 'url' in data and data['url'] and data['url'] != '---':
        message_parts.append(f"\n🔗 <a href='{data['url']}'>Подробнее</a>")

    return "\n".join(message_parts)


def build_message_with_description(data):
    """Собирает текст сообщения только с названием и описанием."""
    message_parts = []
    
    if 'Название' in data and data['Название']:
        message_parts.append(f"🎬 <b>{data['Название']}</b>")
    
    if 'Описание' in data and data['Описание']:
        message_parts.append(f"📝 {data['Описание']}")

    message = "\n\n".join(message_parts)

    max_length = 1024
    if len(message) > max_length:
        message = message[:max_length - 10] + "...\n(Обрезано)"

    return message


def send_poster_with_info(bot_token, chat_id, info_file_path, image_folder):
    """Отправляет постер с основной информацией о фильме."""
    send_photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    poster_path = os.path.join(image_folder, "poster.jpg")
    
    if not os.path.exists(poster_path):
        print_error("[send_poster_with_info] Постер не найден.")
        return False

    data = parse_info_file(info_file_path)
    caption = build_message_without_description(data)

    try:
        with open(poster_path, "rb") as poster_file:
            response = requests.post(
                send_photo_url,
                data={
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": "HTML"
                },
                files={"photo": poster_file}
            )

        if response.status_code != 200:
            print_error(f"[send_poster_with_info] Ошибка отправки: {response.status_code} - {response.text}")
            return False
        return True

    except Exception as e:
        print_error(f"[send_poster_with_info] Ошибка при отправке постера: {e}")
        return False


def send_photos_with_captions(bot_token, chat_id, info_file_path, image_folder, images_list):
    """Отправляет остальные фотографии с названием и описанием."""
    # Сначала отправляем постер с информацией
    if not send_poster_with_info(bot_token, chat_id, info_file_path, image_folder):
        return

    # Затем отправляем остальные фотографии
    send_media_url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
    
    # Исключаем poster.jpg из списка изображений
    images_list = [img for img in images_list if img.lower() != "poster.jpg"]
    
    if not images_list:
        return

    media_group = []
    files = {}

    for idx, image_filename in enumerate(images_list):
        image_path = os.path.join(image_folder, image_filename)
        if os.path.exists(image_path):
            attach_name = f"file{idx}"
            files[attach_name] = open(image_path, "rb")
            media_item = {
                "type": "photo",
                "media": f"attach://{attach_name}"
            }
            if idx == 0:  # Добавляем подпись только к первому изображению
                msg = build_message_with_description(parse_info_file(info_file_path))
                media_item["caption"] = msg
                media_item["parse_mode"] = "HTML"
            media_group.append(media_item)
        else:
            print_error(f"[send_photos_with_captions] Изображение {image_filename} не найдено в папке.")

    if not media_group:
        print_error(f"[send_photos_with_captions] Нет изображений для отправки.")
        return

    try:
        response = requests.post(
            send_media_url,
            data={"chat_id": chat_id, "media": json.dumps(media_group)},
            files=files
        )

        if response.status_code != 200:
            print_error(f"[send_photos_with_captions] Ошибка отправки: {response.status_code} - {response.text}")

    except Exception as e:
        print_error(f"[send_photos_with_captions] Ошибка при отправке фотографий: {e}")
    finally:
        for file in files.values():
            file.close()
