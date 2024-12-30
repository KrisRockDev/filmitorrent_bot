
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