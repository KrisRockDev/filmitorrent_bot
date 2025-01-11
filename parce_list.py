import os
import time
import shutil
import datetime
import requests
from icecream import ic
from bs4 import BeautifulSoup
from send_message import telegram_sender
from download_files import get_urls_bin_files
from settings import filmitorrent, films_list_base, DEBUG, base_dir


def del_dir():
    lst = os.listdir(base_dir)
    limit = 10
    if len(lst) > limit:
        del_list = lst[:-1 * limit]
        for item in del_list:
            folder_path = os.path.join(base_dir, item)  # удаление папки
            # Проверяем, существует ли папка
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # Удаляем папку и все её содержимое
                shutil.rmtree(folder_path)


def create_base_dir():
    if base_dir not in os.listdir():
        os.mkdir(base_dir)


def create_film_dir(title):
    create_base_dir()
    if title not in os.listdir(base_dir):
        os.mkdir(os.path.join(base_dir, title))
    print(title)
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
        print(f"Ошибка при загрузке страницы: {e}")
        return None


def parse_page():
    get_films_list()

    link_list = os.listdir(base_dir)
    for item in link_list:
        link = filmitorrent + f'/{item}.html'

        get_image(link)


if __name__ == '__main__':
    parse_page()
