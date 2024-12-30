from bs4 import BeautifulSoup
import requests
import datetime
import os
# from icecream import ic
from tqdm import tqdm
import shutil
import requests
# from bash import bash


def send_message(txt, image_path):
    # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
    TOKEN = ''

    # Замените 'chat_id' на ID чата, в который вы хотите отправить сообщение
    chat_id = [
        "671116551",
    ]

    # URL для отправки сообщений через Telegram Bot API
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
    with open(txt, mode='r', encoding='utf-8') as discription:
        message_text = discription.read()

    res_txt = ''
    for i in message_text:
        word_list = ['✅Опубликовано:', '🔗url:']
        if i.split(' ')[0] not in word_list:
            res_txt += i

    # Отправка изображения с текстом
    for chat_id_item in chat_id:
        with open(image_path, 'rb') as image_file:
            response = requests.post(url, data={'chat_id': chat_id_item, 'caption': res_txt}, files={'photo': image_file})

    # Проверка ответа
    # if response.status_code == 200:
    # print('Сообщение с изображением успешно отправлено.')
    # else:
    #     print('Ошибка при отправке сообщения с изображением:', response.text)


def save_bin_files(URL, filmitorrent, folder_dir, DIR):
    u = URL
    response = requests.get(u)

    # Создать объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Получить ссылку на изображение
    poster = soup.find('div', class_='poster-big')
    img_src = poster.find('img')['src']

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
    for torrent_link in torrent_links[::-1]:
        if torrent_link.find('1080') > -1:
            torrent_file = torrent_link

    file_response = requests.get(filmitorrent[:-1] + torrent_file)
    source_file = os.path.join(folder_dir, os.path.split(torrent_file)[1])  # 'путь_к_исходному_файлу'
    with open(source_file, 'wb') as f:
        f.write(file_response.content)

    # Копирование файла *torrent
    # if folder_dir.lower().find('сериал') == -1:
    #     shutil.copy(source_file, DIR)

    send_message(txt=os.path.join(folder_dir, 'Описание.txt'), image_path=os.path.join(folder_dir, 'poster.jpg'))


def get_date(film_dict):
    # обработка даты публикации для названия папки
    date = film_dict['Опубликовано:'].lower()
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
    return [date[0].replace('-', '.'), date[1]]


def wite_log(DIR, folder_name, log_file_name):
    with open(os.path.join(DIR, log_file_name), 'a+', encoding='utf-8') as file:
        file.write(folder_name + '\n')


def wite_log_starts(DIR):
    with open(os.path.join(DIR, 'log_starts.txt'), 'a+', encoding='utf-8') as file:
        file.write(str(datetime.datetime.now()) + '\n')


def create_dir(DIR, film_dict):
    date = get_date(film_dict)
    folder_name = f"{' '.join(date)} {film_dict['Название:']} ({film_dict['Год:']})"

    # проверяем наличие папки
    log_file_name = 'log.txt'
    file_list = []
    f = os.path.join(DIR, log_file_name)
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            file_list = [item.strip() for item in file.readlines()]
        # print(file_list)

    if folder_name not in file_list[::-1]:
        wite_log(DIR, folder_name, log_file_name)

        if folder_name not in os.listdir(DIR):
            folder_dir = os.path.join(DIR, folder_name)
            os.mkdir(folder_dir)
            file_name = os.path.join(folder_dir, 'Описание.txt')
            text_data = f'''Опубликовано: {' '.join(date)}\n'''

            # сохраняем данные в файл
            for item in film_dict:
                text_data += f'{item} {film_dict[item]}\n'
            text_data = text_data.replace('Время', '🕒Продолжительность').replace('Название', '🎥Название').replace(
                'Рейтинг: 0\n', '').replace('Рейтинг', '💥Рейтинг', ).replace('Актеры', '🤡Актеры', ).replace(
                'Режиссер', '👤Режиссер', ).replace('Страна', '🚩Страна', ).replace('Год', '📅Год', ).replace(
                'Жанр', '📌Жанр', ).replace('Опубликовано', '✅Опубликовано', ).replace('url', '🔗url', )
            with open(file=file_name, mode='w', encoding='utf-8') as file:
                file.write(text_data)

            return film_dict, folder_dir
        else:
            return None, None
    else:
        return None, None


def parser(FILMITORRENT):
    res_list = []
    response = requests.get(FILMITORRENT)
    soup = BeautifulSoup(response.text, 'html.parser')

    frate_kps = soup.find_all('div', {'class': 'frate frate-kp'})
    post_stories = soup.find_all('div', {'class': 'post-story'})
    datas = soup.find_all('div', {'class': 'data'})
    post_titles = soup.find_all('div', {'class': 'post-title'})

    for num, post_title in enumerate(post_titles):
        data_dict = {}
        movie_title = post_title.text.strip()

        data = datas[num].find('span', {'class': 'cell'})
        # print(f'Название: {movie_title}\nРейтинг: {frate_kps[num].text}')
        # print(f'Опубликовано: {data.text.strip()}')

        link = post_title.find('a')['href']
        # print(f'url: {link}')

        data_dict['Название:'] = movie_title.replace(':', '.')
        data_dict['Рейтинг:'] = frate_kps[num].text
        data_dict['Опубликовано:'] = data.text.strip()
        data_dict['url:'] = link

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

        res_list.append(data_dict)
    return res_list


def main():
    USER = ''
    PASS = ''
    # bash(rf'sudo mount -t cifs -o username={USER},password={PASS} //192.168.1.40/video /home/pi/nas/films')
    # bash(rf'sudo mount -t cifs -o username={USER},password={PASS} //192.168.1.40/Trash /home/pi/nas/trash')

    FILMITORRENT = 'http://filmitorrent.net/'
    DIR = r'd:\filmtorrent'
    # DIR = r'/home/pi/filmtorrent'
    # DIR = r'/home/pi/nas/films/Films'
    wite_log_starts(DIR)

    films_list = parser(FILMITORRENT)

    for film_dict in tqdm(films_list[::-1], ncols=80):
        film_dict, folder_dir = create_dir(DIR, film_dict)
        if film_dict:
            save_bin_files(film_dict['url:'], FILMITORRENT, folder_dir, DIR)


if __name__ == '__main__':
    main()
#