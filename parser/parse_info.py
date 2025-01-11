import os
import time
import shutil
import datetime
from icecream import ic
import html
import requests
from settings import *
from bs4 import BeautifulSoup
from logger import print_error

def get_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим блок div с классом film-info
    film_info_div = soup.find("div", class_="film-info")

    rep_list = [
        ('Название:', '\nНазвание:'),
        ('Оригинальное название:', '\nОригинальное название:'),
        ('Год:', '\nГод:'),
        ('Продолжительность:', '\nПродолжительность:'),
        ('Страна:', '\nСтрана:'),
        ('Рейтинг:', '\nРейтинг:'),
        ('Режиссер:', '\nРежиссер:'),
        ('Актеры:', '\nАктеры:'),
        ('Жанр:', '\nЖанр:'),
        ('Опубликовано:', '\nОпубликовано:'),
        ('Дата выхода в России:', '\nДата выхода в России:'),
        ('Премьера в мире:', '\nПремьера в мире:'),
        (' , ', ', '),
        (': ', ':'),
        ('  ', ' '),
        (' \n', '\n'),
        ('\xa0', ''),
    ]

    # 2024, &nbsp;«Атмосфера

    if film_info_div:
        # Извлекаем текст только из этого блока
        text = film_info_div.get_text(separator=" ", strip=True)

        for item in rep_list:
            text = text.replace(item[0], item[1])
        text += f'\nurl:{url}'
        film_name = os.path.basename(url).split('.')[0]
        film_dir = os.path.join(base_dir_absolute, film_name)
        file = os.path.join(film_dir, 'info.txt')

        if not os.path.exists(file):
            with open(file=file, mode='w', encoding='utf-8') as f:
                f.write(text)
            # print(f'Файл info.txt создан для {film_name}')
        else:
            # print(f'Файл info.txt уже есть для {film_name}')
            pass
    else:
        print_error(f"[get_info] {url} Блок film-info не найден")
