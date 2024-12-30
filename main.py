from bs4 import BeautifulSoup
import requests
import datetime
import os
from icecream import ic
import time

DIR = r'd:\filmtorrent'


def save_pic(URL, filmitorrent, folder_dir):
    u = URL
    print(u)
    response = requests.get(u)

    # Создать объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Получить ссылку на изображение
    poster = soup.find('div', class_='poster-big')
    img_src = poster.find('img')['src']
    ic(img_src)
    # Сохранить изображение в файл
    img_response = requests.get(filmitorrent[:-1] + img_src)
    with open(os.path.join(folder_dir, 'poster.jpg'), 'wb') as f:
        f.write(img_response.content)

    # Получить ссылки на файлы *.torrent
    torrent_links = []
    table = soup.find('table', class_='res85gtj')
    rows = table.find_all('tr')[1:]  # пропустить заголовок таблицы
    for row in rows:
        cells = row.find_all('td')
        link = cells[-1].find('a')['href']
        torrent_links.append(link)

    # Вывести список ссылок на файлы *.torrent
    torrent_file = torrent_links[-1]
    print(torrent_links)
    for torrent_link in torrent_links[::-1]:
        if torrent_link.find('1080') > -1:
            torrent_file = torrent_link

    file_response = requests.get(filmitorrent[:-1] + torrent_file)
    with open(os.path.join(folder_dir, os.path.split(torrent_file)[1]), 'wb') as f:
        f.write(img_response.content)


def create_dir(data_dict, filmitorrent):
    date = data_dict['Опубликовано:'].lower()
    if date.find('сегодня') > -1:
        today = str(datetime.date.today())
        date = [today, date.split(',')[1].strip().replace(':', '-')]
    elif date.find('вчера') > -1:
        today = datetime.date.today()
        yesterday = str(today - datetime.timedelta(days=1))
        date = [yesterday, date.split(',')[1].strip().replace(':', '-')]
    else:
        date_day = '-'.join(date.split(',')[0].split('-')[::-1])
        if len(date_day) == 9:
            date_day = f'{date_day[:-1]}0{date_day[-1]}'
        date = [date_day, date.split(',')[1].strip().replace(':', '-')]

    folder_name = f"{' '.join(date)} {data_dict['Название:']}"

    if folder_name not in os.listdir(DIR):
        print(folder_name)
        folder_dir = os.path.join(DIR, folder_name)
        os.mkdir(folder_dir)
        file_name = os.path.join(folder_dir, 'Описание.txt')
        text_data = f'''Опубликовано: {' '.join(date)}\n'''

        for item in data_dict:
            if item != 'Опубликовано:':
                text_data += f'{item} {data_dict[item]}\n'
        with open(file=file_name, mode='w', encoding='utf8') as file:
            file.write(text_data)

        save_pic(data_dict['url:'], filmitorrent, folder_dir)


def films_list(data_dict):
    url = data_dict['url:']
    films_list_base = 'films_list.txt'

    if not os.path.exists(films_list_base):
        with open(file=films_list_base, mode='w', encoding='utf8') as f:
            f.write('')

    with open(file=films_list_base, mode='r', encoding='utf8') as f:
        lst = f.read().strip()
        lst = lst.split('\n')

    if url not in lst:
        lst.append(url)
        if len(lst) > 20:
            lst = lst[-20:]
            with open(file=films_list_base, mode='w', encoding='utf8') as f:
                f.write('\n'.join(lst) + '\n')
        else:
            with open(file=films_list_base, mode='a', encoding='utf8') as f:
                f.write(url + '\n')

        # send_message(data_dict)


def parse_func():
    filmitorrent = 'http://filmitorrent.net/'
    response = requests.get(filmitorrent)
    soup = BeautifulSoup(response.text, 'html.parser')

    frate_kps = soup.find_all('div', {'class': 'frate frate-kp'})
    post_stories = soup.find_all('div', {'class': 'post-story'})
    datas = soup.find_all('div', {'class': 'data'})
    post_titles = soup.find_all('div', {'class': 'post-title'})

    for num, post_title in enumerate(post_titles):
        data_dict = {}
        movie_title = post_title.text.strip()
        if movie_title.lower().find('сериал') == -1:
            data = datas[num].find('span', {'class': 'cell'})
            link = post_title.find('a')['href']
            data_dict['Название:'] = movie_title.replace(':', '.')
            data_dict['Рейтинг:'] = frate_kps[num].text
            data_dict['Опубликовано:'] = data.text.strip()
            data_dict['url:'] = link

            # Актеры
            post_story = post_stories[num]
            for b in post_story.find_all('b'):
                key = b.text.strip()
                value = []
                for sibling in b.next_siblings:
                    if sibling.name == 'br':
                        break
                    if sibling.name == 'a':
                        value.append(sibling.text)
                    elif isinstance(sibling, str):
                        value.append(sibling.strip())
                line = []
                for val in value:
                    if val not in ['', ',']:
                        line.append(val)
                data_dict[key] = ', '.join(line)

            films_list(data_dict)
            ic(data_dict)


if __name__ == '__main__':
    # while True:
    #     parse_func()
    #     time.sleep(1800)

    parse_func()
