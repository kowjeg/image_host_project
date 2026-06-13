from .db import get_connection
import logging


def save_metadata(filename: str, original_name: str, size: int, file_type: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            sql = '''INSERT INTO images(filename, original_name, size, file_type)
            VALUES (%s, %s, %s, %s)'''
            cursor.execute(sql, (filename, original_name, size, file_type))
            logging.info(f'БД: метаданные для {filename} сохранены')



def get_images(per_page: int, offset: int) -> None:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT id, filename, original_name, size, upload_time, file_type
                FROM images
                ORDER BY upload_time DESC
                LIMIT %s OFFSET %s
                ''', (per_page, offset))
                rows = cursor.fetchall()
        return rows
    except Exception as e:
        logging.error('Не смогли получить данные')
        raise

def get_count_images():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM images')
                total = cursor.fetchone()[0]
                return total
    except Exception as e:
        logging.error('Не смогли получить данные')
        raise


def delete_image_by_id(image_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT filename FROM images WHERE id = %s', (image_id,))
            row = cursor.fetchone()
            if row is None:
                logging.warning(f'БД: запись с id={image_id} не найдена')
                return None
            cursor.execute('DELETE FROM images WHERE id = %s', (image_id,))
            logging.info(f'БД: запись id={image_id} ({row[0]}) удалена')
            return row[0]
