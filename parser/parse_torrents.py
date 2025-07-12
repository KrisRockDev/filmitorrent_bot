import os
import time
import shutil
import datetime
import html
from icecream import ic
import requests
from bs4 import BeautifulSoup
from settings import base_dir_absolute, filmitorrent  # Keep only necessary imports from settings
from logger import print_error


# Added s (session) and film_dir as parameters, and is_update_check
def get_torrents(url, s, film_dir, is_update_check=False):
    # film_name is derived from film_dir in torrent_updater, so os.path.basename(url) is not needed here for film_name
    # id_film = film_name.split('-')[0] # Not used

    # Папка для сохранения изображений - film_dir is now passed as an argument
    os.makedirs(film_dir, exist_ok=True)

    available_torrent_filenames = []
    processed_any_torrents = False

    try:
        response = s.get(url)  # Use the passed session object 's'
        response.raise_for_status()
    except requests.RequestException as e:
        print_error(f"[get_torrents] Request failed for {url}: {e}")
        return None  # Return None on error as discussed for torrent_updater

    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлечение информации и скачивание файлов
    rows = soup.select("tbody tr")
    if not rows:
        ic(f"No torrent rows found on {url}")
        # Still return empty list, not None, as the page might be valid but empty
        return available_torrent_filenames

    for row in rows:
        processed_any_torrents = True
        try:
            # Извлекаем данные из строки
            # number = row.find("td").text.strip() # Not used
            # title = row.find("td").find("b").text.strip() # Not used
            size_cell = row.find_all("td")
            if len(size_cell) < 3:
                ic(f"Skipping row, not enough cells: {row}")
                continue
            size = size_cell[2].text.strip()
            size_ = size.replace('\xa0GB', 'Gb').replace('\xa0MB', 'Mb')  # Handle MB as well
            # seeds = row.find_all("td")[3].text.strip() # Not used
            # peers = row.find_all("td")[4].text.strip() # Not used

            torrent_anchor = row.find("a", class_="safapp")
            if not torrent_anchor or not torrent_anchor.get("href"):
                ic(f"Skipping row, no torrent link found: {row}")
                continue
            torrent_link = torrent_anchor.get("href")

            # Формируем полный URL для скачивания торрент-файла
            # Ensure filmitorrent ends with a slash if torrent_link doesn't start with one
            if filmitorrent.endswith('/') and torrent_link.startswith('/'):
                torrent_url = filmitorrent + torrent_link[1:]
            elif not filmitorrent.endswith('/') and not torrent_link.startswith('/'):
                torrent_url = filmitorrent + '/' + torrent_link
            else:
                torrent_url = filmitorrent + torrent_link

            file_name = os.path.basename(torrent_link).replace('.torrent', f'.size.{size_}.torrent')
            file_path = os.path.join(film_dir, file_name)

            # Скачивание торрент-файла
            if not os.path.exists(file_path):
                ic(f"Downloading new torrent: {file_name} from {torrent_url}")
                try:
                    torrent_response = s.get(torrent_url, stream=True)  # Use session 's'
                    torrent_response.raise_for_status()
                    with open(file_path, "wb") as file:
                        for chunk in torrent_response.iter_content(1024):
                            file.write(chunk)
                    ic(f"Torrent downloaded: {file_name}")
                except requests.RequestException as e:
                    print_error(f"[get_torrents] {url} Ошибка скачивания торрент-файла {torrent_url}: {e}")
                    # If download fails, we might not want to add it to available_torrent_filenames
                    # or handle it differently. For now, skip adding if download fails.
                    continue

            available_torrent_filenames.append(file_name)

        except Exception as e:
            # Log error for this specific row and continue with others
            print_error(f"[get_torrents] Error processing a row for {url}: {e}. Row: {row}")
            continue  # Continue to next row

    if not is_update_check and processed_any_torrents:
        try:
            with open(os.path.join(film_dir, 'new'), mode='w', encoding='utf-8') as f:
                f.write('')
            ic(f"'new' file created for {film_dir} as it's an initial scan with torrents.")
        except IOError as e:
            print_error(f"[get_torrents] Error creating 'new' file for {film_dir}: {e}")

    return available_torrent_filenames

