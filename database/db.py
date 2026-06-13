import psycopg
import os


def get_connection():
    return psycopg.connect(
        dbname='images_db',
        user='postgres',
        password='postgres',
        host='db',
        port='5432'
    )