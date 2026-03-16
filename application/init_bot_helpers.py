from telebot.states import State, StatesGroup
from telebot import types


class Command:
    TEACH = "Практиковаться"
    SHOW_WORDS = "Показать все слова"
    ADD_WORD = "Добавить новое слово"
    DELETE_WORD = "Удалить слово"
    NEXT = "Дальше ⏭"
    BACK = "Назад"


class MyStates(StatesGroup):
    correct_en = State()
    correct_ru = State()
    wrong_words = State()


def get_btns_start():
    """creatted buttons"""
    btns = [
        Command.TEACH,
        Command.SHOW_WORDS,
        Command.ADD_WORD,
        Command.DELETE_WORD,
    ]
    return [types.KeyboardButton(btn) for btn in btns]


def get_btns_teach():
    """creatted buttons"""
    btns = [
        Command.NEXT,
        Command.SHOW_WORDS,
        Command.ADD_WORD,
        Command.DELETE_WORD,
    ]
    return [types.KeyboardButton(btn) for btn in btns]


def show_target(data):
    return f"{data['correct_en']} -> {data['correct_ru']}"


def show_hint(*lines):
    return "\n".join(lines)
