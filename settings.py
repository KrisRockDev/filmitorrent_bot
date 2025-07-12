import os

# Сайт с новинками кино
filmitorrent = 'http://filmitorrent.net/'

# файл со списком фильмов, для исключения отправки повторного уведомления
films_list_base = 'films_list.txt'

# файл для добавления новых пользователей (CHAT_ID)
users_file = 'users.txt'

dirs = [
    base_dir := 'downloads',  # директория для скачивания
    users_dir := 'users',  # директория с пользователями
    log_dir := 'logs',  # директория для логов
]

# директория с пользователями
users_dir_absolute = os.path.abspath(users_dir)

# директория для скачивания
base_dir_absolute = os.path.abspath(base_dir)

# директория для логов
log_dir_absolute = os.path.abspath(log_dir)

# Количество фильмов сохраняемх в папке base_dir (не рекомендуется менее 10 и более 100)
limit = 10

# Переменная для режима отладки
# True - запуск бота в режиме отладки для однократного запуска
# False - запуск бота в режиме реальной работы для периодического парсинга сайта
# DEBUG = False
DEBUG = True

# ID канала для отправки сообщений
CHANNEL_ID = os.getenv("CHANNEL_ID")

# файл для хранения информации об отправленных сообщениях
POSTED_MESSAGES_DB = 'posted_messages.json'
