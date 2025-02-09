import os
import time
import shutil
import datetime
import requests
from icecream import ic
from bs4 import BeautifulSoup
from settings import *
from parser.parse_info import *
from parser.parse_poster import *
from parser.parse_des import *
from parser.parse_img import *
from parser.parse_torrents import get_torrents
from logger import print_error


def del_dir():
    lst = os.listdir(base_dir)
    if len(lst) > limit:
        del_list = lst[:-1 * limit]
        for item in del_list:
            folder_path = os.path.join(base_dir, item)  # удаление папки
            # Проверяем, существует ли папка
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # Удаляем папку и все её содержимое
                shutil.rmtree(folder_path)


def create_dir(dir):
    if dir not in os.listdir():
        os.mkdir(dir)


def create_film_dir(title):
    create_dir(base_dir)
    if title not in os.listdir(base_dir):
        os.mkdir(os.path.join(base_dir, title))
    # print(f"{title=}")
    del_dir()
    return title


def get_films_list():
    try:
        # Выполняем запрос к странице
        response = requests.get(filmitorrent)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")  # Парсим HTML
        post_titles = soup.find_all("div", class_="post-title")  # Находим все элементы <div class="post-title">

        # Сохраняем ссылки и текст
        results = []
        for post_title in reversed(post_titles):  # reversed() реверсирует список
            link_tag = post_title.find("a")
            if link_tag:
                link = link_tag["href"]
                title = os.path.basename(link).split('.')[0]
                create_film_dir(title)
                text = link_tag.text.strip()
                results.append({"link": link, "text": text})
        return results

    except requests.exceptions.RequestException as e:
        print_error(f"[get_films_list] {filmitorrent} Ошибка при загрузке страницы: {e}")
        return None


def check_url(url):
    try:
        response = requests.get(url)
        # Если статус код 200, ссылка работает
        if response.status_code == 200:
            return True
        else:
            print_error(f"[check_url] {url} Ошибка: {url} вернул статус код {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        # В случае исключений (например, неправильный URL или нет соединения)
        print_error(f"[check_url] {url} Ошибка при проверке ссылки {url}: {e}")
        return False


def parse_page():
    for dir in dirs:
        create_dir(dir)

    get_films_list()

    link_list = os.listdir(base_dir)
    c = len(link_list)
    for num, item in enumerate(link_list):
        link = filmitorrent + f'/{item}.html'

        if check_url(link):
            print(f'{num+1}/{c} Обрабатываю {item}')
            get_image(link)
            print(f'- Постер загружен')
            get_info(link)
            print(f'- Информация загружена')
            get_des(link)
            print(f'- Описание загружено')
            get_img(link)
            print(f'- Фрагменты загружены')
            get_torrents(link)
            print(f'- Файлы торрент загружены')
    ic('Программа завершила работу')


if __name__ == '__main__':
    parse_page()
