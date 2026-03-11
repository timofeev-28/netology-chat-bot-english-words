from pathlib import Path
from get_conn import get_db_connection


def create_db():
    """Creating tables in the database"""
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        current_dir = Path(__file__).parent
        sql_file_path = current_dir / "create_tables.sql"

        with open(sql_file_path, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()

        cursor.execute(sql_script)
        conn.commit()
        print("Tables success created!")
    except (FileNotFoundError, IOError):
        print("Файл 'create_tables.sql' не найден или повреждён")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
