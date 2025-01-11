import requests
from settings import *
from bs4 import BeautifulSoup
from logger import print_error


def get_des(url):
    film_name = os.path.basename(url).split('.')[0]
    id_film = film_name.split('-')[0]
    film_dir = os.path.join(base_dir_absolute, film_name)
    file = os.path.join(film_dir, 'des.txt')

    # Парсим HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим нужный блок div по id
    news_div = soup.find("div", id=f"news-id-{id_film}")

    if news_div:
        # Извлекаем текст из блока и очищаем
        raw_text = news_div.get_text(separator=" ", strip=True)
        text = raw_text.replace("\u00a0", " ")  # Убираем &nbsp; (заменяем на пробел)
        if not os.path.exists(file):
            with open(file=file, mode='w', encoding='utf-8') as f:
                f.write(text)
            # print(f'Файл des.txt создан для {film_name}')
        else:
            # print(f'Файл des.txt уже есть для {film_name}')
            pass
    else:
        print_error(f"[get_des] {url} Блок с id 'news-id-{id_film}' не найден.")
