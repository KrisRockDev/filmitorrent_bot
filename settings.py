import os

# Сайт с новинками кино
filmitorrent = 'http://filmitorrent.net/'

# файл со списком фильмов, для исключения отправки повторного уведомления
films_list_base = 'films_list.txt'

# файл для добавления новых пользователей (CHAT_ID)
users_file = 'users.txt'

# директория с пользователями
users_dir = 'users'
users_dir_absolute = os.path.abspath(users_dir)

# директория для скачивания
base_dir = 'downloads'
base_dir_absolute = os.path.abspath(base_dir)

# Переменная для режима отладки
# True - запуск бота в режиме отладки для однократного запуска
# False - запуск бота в режиме реальной работы для периодического парсинга сайта
DEBUG = False
# DEBUG = True