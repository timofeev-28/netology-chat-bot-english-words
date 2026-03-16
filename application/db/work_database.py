from application.db.create_db import get_db_connection


def get_or_create_user(telegram_id, username="User"):
    """checking for the presence of the user in the database, if not, creates."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE tg_id = %s", (telegram_id,)
            )
            user = cursor.fetchone()

            if not user:
                cursor.execute(
                    "INSERT INTO users (tg_id, name) VALUES (%s, %s) RETURNING id;",
                    (telegram_id, username),
                )
                user = cursor.fetchone()
                conn.commit()
            return user[0] if user else None
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return None
    finally:
        conn.close()


def get_random_word(user_id):
    """getting a random word"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT w.id, w.word_ru, w.word_en
            FROM words w
            LEFT JOIN users_words uw ON uw.word_id = w.id
            WHERE w.is_common = TRUE 
               OR uw.user_id = %s
            ORDER BY RANDOM() LIMIT 1
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()


def get_wrong_words(correct_word_id, limit=3):
    """getting 3 incorrect answers"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT w.word_en
            FROM words w
            WHERE w.id != %s
            ORDER BY RANDOM() LIMIT %s
            """
            cursor.execute(query, (correct_word_id, limit))
            result = cursor.fetchall()
            return [r[0] for r in result]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


def get_all_words(user_id):
    """getting all words from database"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT DISTINCT w.word_en
            FROM words w
            LEFT JOIN users_words uw ON w.id = uw.word_id
            LEFT JOIN users u ON uw.user_id = u.id
            WHERE w.is_common = true OR uw.user_id = user_id
            """
            cursor.execute(query, (user_id))
            result = cursor.fetchall()
        if result:
            return result
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


def add_personal_word(user_id, word_ru, word_en):
    """adding new word"""
    conn = get_db_connection()
    if not conn:
        return (
            "Сбой соединения с базой данных, не удалось добавить слово,"
            "попробуйте ещё раз"
        )

    with conn.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO words (word_ru, word_en, is_common)"
                "VALUES (%s, %s, FALSE)"
                "ON CONFLICT (word_ru, word_en) DO NOTHING RETURNING id",
                (word_ru, word_en),
            )
            result = cursor.fetchone()
            if result:
                word_id = result[0]
            else:
                query = """
                SELECT id
                FROM words
                WHERE word_ru = %s AND word_en = %s
                """
                cursor.execute(query, (word_ru, word_en))
                word_id = cursor.fetchone()[0]  # type: ignore

            cursor.execute(
                "INSERT INTO users_words (user_id, word_id)"
                "VALUES (%s, %s)"
                "ON CONFLICT (user_id, word_id) DO NOTHING RETURNING id",
                (user_id, word_id),
            )
            result_uw = cursor.fetchone()
            if result_uw:
                uw_id = result_uw[0]
                conn.commit()
                query_uw = """
                SELECT w.word_ru
                FROM words w
                LEFT JOIN users_words uw ON w.id = uw.word_id
                WHERE uw.id = %s
                """
                cursor.execute(query_uw, (uw_id,))
                res_add_word = cursor.fetchone()
                return f"Слово '{res_add_word[0]}' добавлено"  # type: ignore
            return f"Слово '{word_ru}' уже есть в базе"

        except Exception as e:
            conn.rollback()
            print(f"Ошибка добавления слова: {e}")
            return "Извините, что-то пошло не так.."
        finally:
            conn.close()


def remove_personal_word(user_id, word):
    """removing word"""
    conn = get_db_connection()
    if not conn:
        return (
            "Сбой соединения с базой данных, не удалось удалить слово,"
            "попробуйте ещё раз"
        )

    with conn.cursor() as cursor:
        try:
            query_uw = """
            SELECT uw.id
            FROM words w
            LEFT JOIN users_words uw ON w.id = uw.word_id
            WHERE uw.user_id = %s AND
                (w.word_ru = %s OR w.word_en = %s)
            """
            cursor.execute(query_uw, (user_id, word, word))
            res = cursor.fetchone()
            if res:
                query_del = """
                DELETE
                FROM users_words
                WHERE id = %s
                """
                cursor.execute(query_del, (res[0],))
                conn.commit()
                return f"Удаление слова '{word}' успешно завершено"
            return f"Слова '{word}' нет среди твоих персональных слов"
        except Exception as e:
            conn.rollback()
            print(f"Ошибка добавления слова: {e}")
            return "Извините, что-то пошло не так.."
        finally:
            conn.close()
