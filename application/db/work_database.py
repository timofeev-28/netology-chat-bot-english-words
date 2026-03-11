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
