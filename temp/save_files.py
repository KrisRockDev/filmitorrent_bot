import requests
from bs4 import BeautifulSoup

# Загрузить страницу
url = "http://filmitorrent.net/komedia/4620-prepody-na-vsyu-golovu-2022.html"
response = requests.get(url)

# Создать объект BeautifulSoup для парсинга HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Получить ссылку на изображение
poster = soup.find('div', class_='poster-big')
img_src = poster.find('img')['src']

# Сохранить изображение в файл
img_response = requests.get(img_src)
with open('poster.jpg', 'wb') as f:
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
print(torrent_links)

# http://filmitorrent.net/torrenti/2/d4/Prepody.na.vsiu.golovu.2022.WEB-DL_46201.torrent

# Этот код использует библиотеки requests и BeautifulSoup для загрузки страницы,
# поиска элементов на странице и извлечения нужных данных.
# Сначала мы ищем блок <div class="poster-big"> и извлекаем ссылку на изображение.
# Затем мы загружаем изображение и сохраняем его в файл с именем "poster.jpg".
# Затем мы ищем таблицу с классом "res85gtj" и извлекаем ссылки на файлы *.torrent из последнего столбца таблицы.
# Наконец, мы выводим список ссылок на файлы *.torrent.
