from telegram import Bot
from telegram import InputFile

# # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
# bot = Bot(token='YOUR_BOT_TOKEN')
#
# # Замените 'chat_id' на ID чата, в который вы хотите отправить сообщение
# chat_id = 'chat_id'
#
# # Отправка изображения
# image_path = 'path_to_your_image.jpg'  # Путь к вашему изображению
# image = InputFile(image_path)
# bot.send_photo(chat_id=chat_id, photo=image, caption='Это ваше изображение')

#
# from telegram.ext import Updater, CommandHandler
#
#
# def start(update, context):
#     chat_id = update.message.chat_id
#     context.bot.send_message(chat_id=chat_id, text=f"Ваш chat_id: {chat_id}")
#
#
# def main():
#     # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
#     updater = Updater(token='6691795210:AAEsBu3kSyKYCaWU1zBv8bZUon08PTMbzGs', use_context=True)
#     dispatcher = updater.dispatcher
#
#     start_handler = CommandHandler('start', start)
#     dispatcher.add_handler(start_handler)
#
#     updater.start_polling()
#     updater.idle()
#
#
# if __name__ == '__main__':
#     main()



# import logging
# import asyncio
# from aiogram import Bot, Dispatcher, types
#
# # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
# API_TOKEN = '6691795210:AAEsBu3kSyKYCaWU1zBv8bZUon08PTMbzGs'
#
# logging.basicConfig(level=logging.INFO)
#
# loop = asyncio.get_event_loop()
# bot = Bot(token=API_TOKEN, loop=loop)
# dp = Dispatcher(bot)
#
# async def on_start(upd: types.Update):
#     chat_id = upd.message.chat.id
#     await upd.message.reply(f"Ваш chat_id: {chat_id}")
#
# @dp.message_handler(commands=['start'])
# async def cmd_start(message: types.Message):
#     await on_start(message)
#
# if __name__ == '__main__':
#     from aiogram import executor
#     executor.start_polling(dp, skip_updates=True)



import requests
# TOKEN = '6691795210:AAEsBu3kSyKYCaWU1zBv8bZUon08PTMbzGs'
# url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
# print(requests.get(url).json())

# chat_id = "671116551"
# message = "Здесь напишите свое сообщение"
# url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
# print(requests.get(url).json()) # Эта строка отсылает сообщение




# import requests
#
# # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
# TOKEN = '6691795210:AAEsBu3kSyKYCaWU1zBv8bZUon08PTMbzGs'
#
# # Замените 'chat_id' на ID чата, в который вы хотите отправить сообщение
# chat_id = "671116551"
#
# # URL для отправки сообщений через Telegram Bot API
# url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
#
# # Путь к файлу изображения, которое вы хотите отправить
# image_path = r'd:\filmtorrent\2023.08.13 17-46 Сердце Стоун (2023)\poster.jpg'
#
# # Отправка изображения
# with open(image_path, 'rb') as image_file:
#     response = requests.post(url, data={'chat_id': chat_id}, files={'photo': image_file})
#
# # Проверка ответа
# if response.status_code == 200:
#     print('Изображение успешно отправлено.')
# else:
#     print('Ошибка при отправке изображения:', response.text)





import requests

# Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
TOKEN = '6691795210:AAEsBu3kSyKYCaWU1zBv8bZUon08PTMbzGs'

# Замените 'chat_id' на ID чата, в который вы хотите отправить сообщение
chat_id = "671116551"

# URL для отправки сообщений через Telegram Bot API
url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'

# Путь к файлу изображения, которое вы хотите отправить
image_path = r'd:\filmtorrent\2023.08.13 17-46 Сердце Стоун (2023)\poster.jpg'

# Текст сообщения
txt = r'd:\filmtorrent\2023.08.13 17-46 Сердце Стоун (2023)\Описание.txt'
with open(txt, mode='r', encoding='utf8') as discription:
    message_text = discription.read()

# Отправка изображения с текстом
with open(image_path, 'rb') as image_file:
    response = requests.post(url, data={'chat_id': chat_id, 'caption': message_text}, files={'photo': image_file})

# Проверка ответа
if response.status_code == 200:
    # print('Сообщение с изображением успешно отправлено.')
    ...
else:
    print('Ошибка при отправке сообщения с изображением:', response.text)
