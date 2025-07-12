import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# Загрузить переменные окружения из .env
load_dotenv()

# ID канала/группы, куда будут отправляться сообщения и комментарии
# Убедитесь, что это ID чата, где разрешены комментарии (например, группа обсуждения канала, или сама группа)
CHANNEL_ID_STR = os.getenv('CHANNEL_ID')

# Токен бота
BOT_TOKEN = os.getenv("TOKEN")

async def main():
    """
    Основная функция для отправки сообщения и комментария.
    """
    if not BOT_TOKEN:
        print("Ошибка: Токен бота (TOKEN) не найден в .env файле.")
        return
    if not CHANNEL_ID_STR:
        print("Ошибка: ID канала/группы (CHANNEL_ID) не найден в .env файле.")
        return

    try:
        # CHANNEL_ID должен быть числом (integer)
        channel_id = int(CHANNEL_ID_STR)
    except ValueError:
        print(f"Ошибка: CHANNEL_ID '{CHANNEL_ID_STR}' должен быть числом.")
        return

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)

    main_message_text = "🤖 Привет! Это автоматическое сообщение от бота."
    comment_text = "💬 А это первый комментарий под сообщением!"

    try:
        # 1. Отправляем основное сообщение
        print(f"Отправка сообщения в чат ID: {channel_id}...")
        sent_message = await bot.send_message(
            chat_id=channel_id,
            text=main_message_text
        )
        message_id = sent_message.message_id
        print(f"Сообщение успешно отправлено! ID сообщения: {message_id}")

        # Небольшая пауза, чтобы Telegram успел обработать (опционально, но иногда полезно)
        await asyncio.sleep(1)

        # 2. Отправляем комментарий (ответ) на это сообщение
        # Комментарий будет отправлен в тот же chat_id, что и основное сообщение.
        # Это работает, если chat_id - это группа или супергруппа,
        # или если это ID группы обсуждения, привязанной к каналу.
        print(f"Отправка комментария к сообщению ID: {message_id} в чат ID: {channel_id}...")
        await bot.send_message(
            chat_id=channel_id,
            text=comment_text,
            reply_to_message_id=message_id
        )
        print("Комментарий успешно отправлен!")

    except TelegramError as e:
        print(f"Произошла ошибка Telegram: {e}")
        print("Пожалуйста, убедитесь, что:")
        print(f"  1. Токен бота '{BOT_TOKEN[:5]}...' валиден.")
        print(f"  2. Бот добавлен в чат/канал с ID {channel_id}.")
        print(f"  3. Бот имеет права на отправку сообщений (и ответов) в этом чате.")
        print(f"  4. Если это канал, и комментарии должны быть в группе обсуждения, то CHANNEL_ID должен быть ID этой группы.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == '__main__':
    # Запуск асинхронной функции main
    asyncio.run(main())