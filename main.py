from application.db.create_db import create_db
from application.init_bot import init_bot


if __name__ == "__main__":
    try:
        print("Инициализация базы данных...")
        create_db()

        print("Запуск бота")
        init_bot()
    except Exception as e:
        print("Error: {e}")
