from .db import get_connection


def create_images():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(100) NOT NULL,
                    original_name VARCHAR(100) NOT NULL,
                    size INTEGER NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type VARCHAR(4) NOT NULL
                )
            """)