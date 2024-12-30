import os
import time
import datetime
import requests
from icecream import ic
from bs4 import BeautifulSoup
from send_message import telegram_sender
from download_files import get_urls_bin_files
from settings import filmitorrent, films_list_base


def convert_word_to_date(word):
    """
    Преобразует слова "Сегодня" и "Вчера" в дату формата "DD-MM-YYYY".
    """
    if word.lower() == "сегодня":
        date = datetime.datetime.now()
        word = date.strftime("%d-%m-%Y")
    elif word.lower() == "вчера":
        date = datetime.datetime.now() - datetime.timedelta(days=1)
        word = date.strftime("%d-%m-%Y")

    return word


def films_list(data_dict):
    url = data_dict['url:']

    if not os.path.exists(films_list_base):
        with open(file=films_list_base, mode='w', encoding='utf8') as f:
            f.write('')

    with open(file=films_list_base, mode='r', encoding='utf8') as f:
        lst = f.read().strip()
        lst = lst.split('\n')

    if url not in lst:
        lst.append(url)
        limit = 20
        if len(lst) > limit:
            lst = lst[-1 * limit:]
            with open(file=films_list_base, mode='w', encoding='utf8') as f:
                f.write('\n'.join(lst) + '\n')
        else:
            with open(file=films_list_base, mode='a', encoding='utf8') as f:
                f.write(url + '\n')

        return get_urls_bin_files(data_dict)
    else:
        return None


def parse_func():
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
            dt, tm = data.text.strip().split(', ')
            data_dict['Опубликовано:'] = f'{convert_word_to_date(dt)}, {tm}'
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

            if data_dict := films_list(data_dict):
                telegram_sender(data_dict)


if __name__ == '__main__':
    # while True:
    #     parse_func()
    #     time.sleep(1800)

    parse_func()
