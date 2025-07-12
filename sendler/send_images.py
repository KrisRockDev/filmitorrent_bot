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
        return None

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

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("ok") and response_data.get("result", {}).get("message_id"):
                return response_data["result"]["message_id"]
            else:
                print_error(f"[send_poster_with_info] Ошибка: message_id не найден в ответе. Ответ: {response.text}")
                return None
        else:
            print_error(f"[send_poster_with_info] Ошибка отправки: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print_error(f"[send_poster_with_info] Ошибка при отправке постера: {e}")
        return None


def send_photos_with_captions(bot_token, chat_id, image_folder, images_list):
    """Отправляет группу изображений без описания."""
    send_media_url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"

    # Исключаем poster.jpg из списка изображений и проверяем, остались ли другие изображения
    images_list = [img for img in images_list if img.lower() != "poster.jpg"]
    if not images_list:
        # ic("[send_photos_with_captions] Нет изображений для отправки (кроме постера).")
        return

    media_group = []
    files = {}

    for idx, image_filename in enumerate(images_list):
        image_path = os.path.join(image_folder, image_filename)
        if os.path.exists(image_path):
            attach_name = f"file{idx}"
            try:
                files[attach_name] = open(image_path, "rb")
                media_item = {
                    "type": "photo",
                    "media": f"attach://{attach_name}"
                }
                media_group.append(media_item)
            except Exception as e:
                print_error(f"[send_photos_with_captions] Ошибка открытия файла {image_filename}: {e}")
        else:
            print_error(f"[send_photos_with_captions] Изображение {image_filename} не найдено в папке.")

    if not media_group:
        # ic("[send_photos_with_captions] Нет медиа для отправки после обработки файлов.")
        # Закрываем файлы, если они были открыты до ошибки
        for file in files.values():
            file.close()
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


def send_stills_with_description_as_reply(bot_token, chat_id, reply_to_message_id, info_file_path, image_folder,
                                          stills_images_list):
    """Отправляет 3 кадра из фильма с полным описанием в ответ на сообщение."""
    send_media_url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"

    if not stills_images_list or len(stills_images_list) != 3:
        print_error("[send_stills_with_description_as_reply] Требуется ровно 3 изображения для кадров.")
        return

    data = parse_info_file(info_file_path)
    caption = build_message_with_description(data)

    media_group = []
    files = {}

    for idx, image_filename in enumerate(stills_images_list):
        image_path = os.path.join(image_folder, image_filename)
        if os.path.exists(image_path):
            attach_name = f"file_still_{idx}"
            try:
                files[attach_name] = open(image_path, "rb")
                media_item = {
                    "type": "photo",
                    "media": f"attach://{attach_name}"
                }
                if idx == 0:  # Добавляем описание к первому кадру
                    media_item["caption"] = caption
                    media_item["parse_mode"] = "HTML"
                media_group.append(media_item)
            except Exception as e:
                print_error(f"[send_stills_with_description_as_reply] Ошибка открытия файла {image_filename}: {e}")
        else:
            print_error(f"[send_stills_with_description_as_reply] Изображение {image_filename} не найдено.")

    if not media_group or len(media_group) != 3:
        print_error("[send_stills_with_description_as_reply] Не удалось подготовить все 3 кадра для отправки.")
        for file in files.values():  # Закрываем открытые файлы перед выходом
            file.close()
        return

    try:
        response = requests.post(
            send_media_url,
            data={
                "chat_id": chat_id,
                "media": json.dumps(media_group),
                "reply_to_message_id": reply_to_message_id
            },
            files=files
        )

        if response.status_code != 200:
            print_error(
                f"[send_stills_with_description_as_reply] Ошибка отправки: {response.status_code} - {response.text}")

    except Exception as e:
        print_error(f"[send_stills_with_description_as_reply] Ошибка при отправке кадров: {e}")
    finally:
        for file in files.values():
            file.close()
