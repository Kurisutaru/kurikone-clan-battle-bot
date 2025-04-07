from dbutils.pooled_db import PooledDB
import mariadb
from config import config


class DatabasePool:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            try:
                cls._pool = PooledDB(
                    creator=mariadb,  # Use pymysql as the driver
                    maxconnections=config.MAX_POOL_SIZE,
                    mincached=2,  # Start with 2 idle connections
                    maxcached=10,  # Max 10 idle connections
                    blocking=True,  # Wait if pool is full
                    host=config.DB_HOST,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=config.DB_PORT
                )
                print(f"Connection pool initialized with size: {config.MAX_POOL_SIZE}")
            except Exception as e:
                print(f"Failed to initialize connection pool: {e}")
                raise
        return cls._instance

    def get_connection(self):
        conn = self._pool.connection()
        return conn

    def __enter__(self):
        return self.get_connection()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"Exception in context: {exc_value}")
        pass


db_pool = DatabasePool()
