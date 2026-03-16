"""the logic of the bot's work"""

import os
import logging
import random
import sys
import telebot
from telebot import custom_filters, types
from dotenv import load_dotenv
from telebot.storage import StateMemoryStorage
from application.db.work_database import (
    add_personal_word,
    get_all_words,
    get_or_create_user,
    get_random_word,
    get_wrong_words,
    remove_personal_word,
)
from application.init_bot_helpers import (
    Command,
    MyStates,
    get_btns_start,
    get_btns_teach,
    show_hint,
    show_target,
)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
try:
    if not BOT_TOKEN:
        raise ValueError("Не найден токен бота! Проверьте файл .env")
    state_storage = StateMemoryStorage()
    bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)
except ValueError as e:
    print(f"Ошибка инициализации: {e}")
    sys.exit(1)


@bot.message_handler(commands=["start"])
def begin_work(message):
    """prompts the user to select an action"""
    get_or_create_user(message.from_user.id, message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*(get_btns_start()))
    welcome_text = (
        f"Привет, {message.from_user.first_name}! \n"
        "Я бот для изучения английских слов.\n"
        "Выбери действие:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.TEACH)
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

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.extend(get_btns_teach())
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


@bot.message_handler(func=lambda message: message.text == Command.BACK)
def go_back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*(get_btns_start()))
    welcome_text = "Выбери действие:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.SHOW_WORDS)
def show_words(message):
    words = get_all_words(message)
    if words:
        text = (
            f"Всего слов (включая общие) на изучении: {len(words)}\n"
            f"\n{", ".join([w[0] for w in words])}"
        )
    else:
        text = "Что-то пошло не так, данные не получены. Попробуйте ещё раз"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*(get_btns_start()))
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_message(message):
    back_btn = types.KeyboardButton(Command.BACK)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(back_btn)
    add_word_text = (
        "Введи новое слово в формате\n"
        "'на русском' - 'на английском',\n"
        "например 'яблоко' - 'apple' и отправь его в сообщении"
    )
    msg = bot.send_message(message.chat.id, add_word_text, reply_markup=markup)
    bot.register_next_step_handler(msg, handle_word)


def handle_word(message):
    user_sql_id = get_or_create_user(message.from_user.id)
    text = message.text
    words = [word.strip().capitalize() for word in text.split("-")]
    if len(words) == 2:
        word_ru, word_en = words
        res = add_personal_word(user_sql_id, word_ru, word_en)
        bot.send_message(message.chat.id, res)
        go_back(message)
    else:
        bot.send_message(
            message.chat.id, "Ошибка: Нужно ввести ровно два слова через тире"
        )
        go_back(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_words(message):
    add_text = (
        "Введи удаляемое слово в любом формате - "
        "или на русском, или на английском,\n\n"
        "например 'яблоко', или 'apple', и отправь его в сообщении"
    )
    msg = bot.send_message(
        message.chat.id, add_text, reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, handle_delete_word)


def handle_delete_word(message):
    user_sql_id = get_or_create_user(message.from_user.id)
    word = (message.text).strip().capitalize()
    res = remove_personal_word(user_sql_id, word)
    bot.send_message(message.chat.id, res)
    go_back(message)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = get_btns_teach()

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:  # type: ignore
        correct_en = data["correct_en"]
        wrong_words = data["wrong_words"]
    if text == correct_en:
        hint = show_target(data)
        hint_text = ["Отлично!❤", hint]
        hint = show_hint(*hint_text)
        markup.add(*buttons)
    else:
        for i, btn in enumerate(wrong_words):
            if btn == text:
                wrong_words[i] = btn + " ❌"
                break
        hint = show_hint(
            "Допущена ошибка!",
            f"Попробуй ещё раз вспомнить слово 🇷🇺{data['correct_ru']}",
        )
        wrong_words.append(correct_en)
        words_en_btns = [types.KeyboardButton(word) for word in wrong_words]
        random.shuffle(words_en_btns)
        markup.add(*words_en_btns, *buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


# =============================================================
def init_bot():
    telebot.logger.setLevel(logging.ERROR)
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
