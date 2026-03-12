"""the logic of the bot's work"""

import os
import logging
import random
import telebot
from telebot import custom_filters, types
from dotenv import load_dotenv
from application.db.work_database import (
    get_or_create_user,
    get_random_word,
    get_wrong_words,
)
from telebot.storage import StateMemoryStorage
from telebot.states import State, StatesGroup


class Command:
    TEACH = "Практиковаться"
    ADD_WORD = "Добавить новое слово"
    DELETE_WORD = "Удалить слово"
    NEXT = "Дальше ⏭"


class MyStates(StatesGroup):
    correct_en = State()
    correct_ru = State()
    wrong_words = State()


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найден токен бота! Проверьте файл .env")

# ==================================
# used_words: dict[int, list[int]] = {}


# def save_word(user_id, word_id):
#     used_words[user_id].append(word_id)


# ==================================

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)


@bot.message_handler(commands=["start"])
def begin_work(message):
    """prompts the user to select an action"""
    get_or_create_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn_start = types.KeyboardButton(Command.TEACH)
    btn_add = types.KeyboardButton(Command.ADD_WORD)
    btn_delete = types.KeyboardButton(Command.DELETE_WORD)
    markup.add(btn_start, btn_add, btn_delete)

    welcome_text = (
        f"Привет, {message.from_user.first_name}! \n"
        "Я бот для изучения английских слов.\n"
        "Выбери действие"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Практиковаться")
def start_teach(message):
    user_sql_id = get_or_create_user(message.from_user.id)
    word_data = ""
    if user_sql_id:
        word_data = get_random_word(user_sql_id)

    if not word_data:
        bot.send_message(
            message.chat.id,
            "В базе данных пока нет слов, добавьте свои слова!",
        )
        return

    try:
        word_id, correct_ru, correct_en = word_data

        limit_wrong_words = 3
        wrong_words = get_wrong_words(word_id, limit_wrong_words)
        if len(wrong_words) != 3:
            while len(wrong_words) < 3:
                wrong_words.append("FakeWord")

        words_en = wrong_words.copy()
        words_en.append(correct_en)

        buttons = []
        words_en_btns = [types.KeyboardButton(word) for word in words_en]
        buttons.extend(words_en_btns)
        random.shuffle(buttons)
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        buttons.extend([next_btn, add_word_btn, delete_word_btn])

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*buttons)

        greeting = f"Выбери перевод слова:\n🇷🇺 {correct_ru}"
        bot.send_message(message.chat.id, greeting, reply_markup=markup)

        bot.set_state(
            message.from_user.id, MyStates.correct_en, message.chat.id
        )
        state_data = {
            "correct_en": correct_en,
            "correct_ru": correct_ru,
            "wrong_words": wrong_words,
            "word_id": word_id,
        }
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:  # type: ignore
            data.update(state_data)

    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    start_teach(message)


# =============================================================
def init_bot():
    telebot.logger.setLevel(logging.ERROR)
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
