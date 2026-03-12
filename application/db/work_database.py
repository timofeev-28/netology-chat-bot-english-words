from application.db.create_db import get_db_connection


def get_or_create_user(telegram_id):
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
                    "INSERT INTO users (tg_id) VALUES (%s) RETURNING id;",
                    (telegram_id,),
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
    """Getting 3 incorrect answers."""
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
            return [r[0] for r in result] if result else []
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# if __name__ == "__main__":
# print(get_wrong_words(1))
# print(get_random_word(u_id))
