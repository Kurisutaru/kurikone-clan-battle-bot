# database.py
import mariadb
from config import config

class MariaDBConnectionPool:
    def __init__(self):
        self.pool = []
        for _ in range(config['MAX_POOL_SIZE']):
            conn = mariadb.connect(
                host=config['DB_HOST'],
                user=config['DB_USER'],
                password=config['DB_PASSWORD'],
                database=config['DB_NAME'],
                port=config['DB_PORT']
            )
            self.pool.append(conn)

    def get_connection(self):
        if not self.pool:
            raise Exception("No connections available in the pool")
        return self.pool.pop()

    def release_connection(self, conn):
        self.pool.append(conn)

    def __enter__(self):
        return self.get_connection()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.pool:
            self.release_connection(self.pool.pop())
        return False