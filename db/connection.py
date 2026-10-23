import os
from contextlib import contextmanager

import psycopg


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is required.")
    return database_url


@contextmanager
def get_connection():
    conn = psycopg.connect(get_database_url())
    try:
        yield conn
    finally:
        conn.close()
