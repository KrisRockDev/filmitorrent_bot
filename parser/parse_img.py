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


def get_img(url):
    film_name = os.path.basename(url).split('.')[0]
    id_film = film_name.split('-')[0]
    film_dir = os.path.join(base_dir_absolute, film_name)
    # Папка для сохранения изображений
    os.makedirs(film_dir, exist_ok=True)

    # Парсим HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлечение ссылок на изображения и скачивание
    img = soup.find_all("div", class_=f"quote")[-1]
    images = img.find_all("img")

    for img in images:
        img_src = img.get("src")
        if img_src:
            full_url = filmitorrent + img_src  # Формируем полный URL
            file_name = os.path.basename(img_src)  # Имя файла
            file_path = os.path.join(film_dir, file_name)

            if not os.path.exists(file_path):
                # Скачивание изображения
                try:
                    response = requests.get(full_url, stream=True)
                    response.raise_for_status()
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    # print(f"Скачано: {file_name}")
                except Exception as e:
                    print_error(f"[get_img] {url} Ошибка скачивания {file_name}: {e}")
            else:
                # print(f'Файл {file_name} уже сохранён ранее')
                pass
