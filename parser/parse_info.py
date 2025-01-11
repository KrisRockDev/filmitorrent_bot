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


# URL страницы для парсинга
url = "https://example.com"  # Замените на реальный URL

def get_info(url):
    try:
        # Выполняем запрос к странице
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        html_content = response.text

        # Парсим HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Находим блок <div class="film-info">
        film_info_div = soup.find("div", class_="film-info")
        if film_info_div:
            # Извлекаем данные из блока
            def extract_data(label):
                element = film_info_div.find("b", text=label)
                if element:
                    sibling = element.next_sibling
                    return sibling.strip() if sibling else None
                return None

            # Составляем словарь данных
            data = {
                "Жанр": ", ".join([genre.text.strip() for genre in film_info_div.find("span", itemprop="genre").find_all("a")]),
                "Страна": ", ".join([country.text.strip() for country in film_info_div.find_all("a") if "/tags/" in country["href"]]),
                "Название": extract_data("Название:"),
                "Оригинальное название": extract_data("Оригинальное название:"),
                "Режиссер": ", ".join([director.text.strip() for director in film_info_div.find("span", itemprop="director").find_all("a")]),
                "Актеры": ", ".join([actor.text.strip() for actor in film_info_div.find("span", itemprop="actors").find_all("a")]),
                "Премьера в мире": extract_data("Премьера в мире:"),
                "Продолжительность": extract_data("Продолжительность:"),
                "Год": extract_data("Год:")
            }

            # Сохраняем данные в текстовый файл
            with open("info.txt", "w", encoding="utf-8") as file:
                for key, value in data.items():
                    file.write(f"{key}: {value}\n")

            print("Информация успешно сохранена в 'info.txt'")
        else:
            print("Блок <div class='film-info'> не найден.")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
