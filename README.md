# Бот для скачивания торрент-файлов с сайта 'http://filmitorrent.net/'

1. Клонирование репозитория:  
    Склонируйте репозиторий с помощью команды:
    ```sh
    git clone https://github.com/KrisRockDev/filmitorrent_bot.git
    ```
2. Перейдите в директорию:
   Перейдите в директорию tg_echo_bot с помощью команды:
   ```sh
   cd filmitorrent_bot
   ```
   
3. Сборка образа:
   Выполните следующую команду в терминале для создания Docker-образа:
   ```bash
   sudo docker build -t krisrockdev/filmitorrent_bot:2.4 .
   ```

4. Запуск контейнера:
   Запустите контейнер, передав переменную окружения `BOT_TOKEN`:
   ```bash
   sudo docker run -d \
   --restart on-failure \
   -e TOKEN='TELEGRAM-TOKEN' \
   -e CHAT_ID='12345678,910111213' \
   -e DELAY='1800' \
   --name filmitorrent_bot_container_2_4 \
   krisrockdev/filmitorrent_bot:2.4
   ```


### Планы развития
- добавить отправку об ошибках администратору
- добавить управление получателя через бота
- отправку всех фильмов новым пользователям
