import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    DB_CONFIG = {
        'dbname': 'Amazon',
        'user': 'admin',
        'password': '#welcome123',
        'host': 'localhost'
    }

    @staticmethod
    def get_connection():
        return psycopg2.connect(**Database.DB_CONFIG, cursor_factory=RealDictCursor)

    @staticmethod
    def execute_query(query, params=None, fetch=True):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        rows = cur.fetchall() if fetch else None
        conn.commit()
        cur.close()
        conn.close()
        return rows
