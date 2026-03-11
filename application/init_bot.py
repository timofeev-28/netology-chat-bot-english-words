"""the logic of the bot's work"""

import os
import logging
import telebot
from telebot import custom_filters, types
from dotenv import load_dotenv
from application.db.work_database import get_or_create_user


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найден токен бота! Проверьте файл .env")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def begin_work(message):
    """prompts the user to select an action"""
    get_or_create_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn_start = types.KeyboardButton("Начать практиковаться")
    btn_add = types.KeyboardButton("Добавить слово")
    btn_delete = types.KeyboardButton("Удалить слово")
    markup.add(btn_start, btn_add, btn_delete)

    welcome_text = (
        f"Привет, {message.from_user.first_name}! \n"
        "Я бот для изучения английских слов.\n\n"
        "Выбери действие"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


def init_bot():
    telebot.logger.setLevel(logging.ERROR)
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
