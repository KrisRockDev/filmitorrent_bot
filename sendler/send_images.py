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


def build_message(data):
    """Собирает текст сообщения из словаря данных, исключая пустые поля."""
    fields = {
        'Название': "🎬 <b>{}</b>",
        'Оригинальное название': "©️ {}",
        'Жанр': "🎭 Жанр: {}",
        'Год': "🗓 Год: {}",
        'Продолжительность': "⏱ Продолжительность: {}",
        'Страна': "🌍 Страна: {}",
        'Рейтинг': "⭐ Рейтинг: {}",
        'Режиссер': "🎥 Режиссер: {}",
        'Актеры': "🤡 Актеры: {}",
        'Премьера в мире': "🌐 Премьера в мире: {}",
        'Дата выхода в России': "🇷🇺 Дата выхода в России: {}",
        'Описание': "📝 {}"
    }

    message_parts = [fields[key].format(data[key]) for key in fields if
                     key in data and data[key] and data[key] != '---']

    if 'url' in data and data['url'] and data['url'] != '---':
        message_parts.append(f"\n🔗 <a href='{data['url']}'>Подробнее</a>")

    message = "\n".join(message_parts)

    max_length = 1024
    if len(message) > max_length:
        message = message[:max_length - 10] + "...\n(Обрезано)"

    return message

def send_photos_with_captions(bot_token, chat_id, info_file_path, image_folder, images_list):
    """Отправляет медиагруппу с фотографиями и подписью в Telegram."""
    send_media_url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"

    # Подготавливаем файлы и медиа-группу
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

                msg = build_message(parse_info_file(info_file_path))
                media_item["caption"] = msg
                media_item["parse_mode"] = "HTML"
            media_group.append(media_item)
        else:
            print_error(f"[send_photos_with_captions] Изображение {image_filename} не найдено в папке.")

    # Проверяем, есть ли файлы для отправки
    if not media_group:
        print_error(f"[send_photos_with_captions] Нет изображений для отправки.")
        return

    try:
        # Отправляем медиагруппу
        response = requests.post(
            send_media_url,
            data={"chat_id": chat_id, "media": json.dumps(media_group)},
            files=files
        )

        # Проверяем результат запроса
        if response.status_code == 200:
            # print("Фотографии успешно отправлены.")
            pass
        else:
            print_error(f"[send_photos_with_captions] Ошибка отправки: {response.status_code} - {response.text}")

    except Exception as e:
        print_error(f"[send_photos_with_captions] Ошибка при отправке фотографий: {e}")
    finally:
        # Закрываем все открытые файлы
        for file in files.values():
            file.close()
