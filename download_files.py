from bs4 import BeautifulSoup
from icecream import ic
import requests
from settings import filmitorrent


def get_urls_bin_files(data_dict):
    downloads_error = ''
    u = data_dict['url:']
    response = requests.get(u)

    # Создать объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        poster = soup.find('div', class_='poster-big')
        img_src = poster.find('img')['src']
        # Сохранить изображение (постер) в файл
        data_dict['poster'] = filmitorrent[:-1] + img_src
    except Exception as ex:
        downloads_error += f'"[Ошика загрузки постера]" {ex}'

    # Получить ссылки на файлы *.torrent
    try:
        torrent_links = []
        table = soup.find('table', class_='torrent-table')
        rows = table.find_all('tr')[1:]  # пропустить заголовок таблицы
        for row in rows:
            cells = row.find_all('td')
            link = cells[-1].find('a')['href']
            torrent_links.append(link)

        # Вывести список ссылок на файлы *.torrent
        torrent_file = torrent_links[-1]
        for torrent_link in torrent_links[::-1]:
            if torrent_link.find('1080') > -1:
                torrent_file = torrent_link

        data_dict['torrent_file'] = filmitorrent[:-1] + torrent_file
    except Exception as ex:
        downloads_error += f'"[Ошика загрузки торент-файла]" {ex}'

    return data_dict
