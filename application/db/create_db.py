import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from application.db.initial_words import initial_words


load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")


def get_db_connection():
    """Creating a connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT or "5432",
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


def create_tables(conn):
    """Creating tables in the database"""
    cursor = conn.cursor()
    try:
        current_dir = Path(__file__).parent
        sql_file_path = current_dir / "create_tables.sql"

        with open(sql_file_path, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()

        cursor.execute(sql_script)
        conn.commit()
        print("Таблицы успешно созданы!")
        return True
    except (FileNotFoundError, IOError):
        print(
            "Файл 'create_tables.sql' не найден или повреждён\n"
            "Таблицы не созданы"
        )
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}\nТаблицы не созданы")
        return False
    finally:
        cursor.close()


def fill_basic_words(conn):
    """fills the database with basic data"""
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM words WHERE is_common = TRUE")
    count = cursor.fetchone()[0]

    if count == 0:
        if initial_words:
            for ru, en in initial_words:
                cursor.execute(
                    "INSERT INTO words (word_ru, word_en, is_common) VALUES (%s, %s, TRUE)",
                    (ru, en),
                )
            conn.commit()
            cursor.close()
            print("База данных заполнена начальными словами.")
        else:
            print("Нет данных по базовым словам, база не заполнилась.")
    else:
        print("База данных уже заполнена начальными словами")


def create_db():
    """creates and fills the database"""
    conn = get_db_connection()
    if not conn:
        return

    is_tables = create_tables(conn)
    if not is_tables:
        conn.close()
        return

    fill_basic_words(conn)
    conn.close()
