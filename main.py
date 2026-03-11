import telebot
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


if not BOT_TOKEN:
    raise ValueError("Не найден токен бота! Проверьте файл .env")

bot = telebot.TeleBot(BOT_TOKEN)



if __name__ == "__main__":
    # print("Бот запущен...")
    # print("Для завершения нажмите Ctrl+Z")
    # bot.polling()  # запускаем бота, данный метод постоянно ожидает сообщения для бота
