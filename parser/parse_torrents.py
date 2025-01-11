import os
import time
import shutil
import datetime
import html
from icecream import ic
import requests
from bs4 import BeautifulSoup
from settings import *
from logger import print_error

def get_torrents(url):
    film_name = os.path.basename(url).split('.')[0]
    id_film = film_name.split('-')[0]
    film_dir = os.path.join(base_dir_absolute, film_name)
    # Папка для сохранения изображений
    os.makedirs(film_dir, exist_ok=True)

    # Парсим HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлечение информации и скачивание файлов
    rows = soup.select("tbody tr")
    for row in rows:
        # Извлекаем данные из строки
        number = row.find("td").text.strip()
        title = row.find("td").find("b").text.strip()
        size = row.find_all("td")[2].text.strip()
        size_ = size.replace('\xa0GB', 'Gb')
        seeds = row.find_all("td")[3].text.strip()
        peers = row.find_all("td")[4].text.strip()
        torrent_link = row.find("a", class_="safapp").get("href")

        # Формируем полный URL для скачивания торрент-файла
        torrent_url = filmitorrent + torrent_link

        # Скачивание торрент-файла
        try:
            response = requests.get(torrent_url, stream=True)
            response.raise_for_status()
            file_name = os.path.basename(torrent_link).replace('.torrent', f'.size.{size_}.torrent')
            file_path = os.path.join(film_dir, file_name)
            if not os.path.exists(file_path):
                # Скачивание torrent файла
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                with open(os.path.join(film_dir, 'new'), mode='w', encoding='utf-8') as f:
                    f.write('')
                # print(f"Торрент скачан: {file_name}")
        except Exception as e:
            print_error(f"[get_torrents] {url} Ошибка скачивания торрент-файла: {e}")

        # Печать информации о раздаче
        # print(f"""
        # №: {number}
        # Название: {title}
        # Размер: {size}
        # Сиды: {seeds}
        # Пиры: {peers}
        # Торрент-файл: {file_name}
        # """)

