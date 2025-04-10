from functools import wraps
from database import db_pool


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = db_pool.get_connection()
            result = await func(*args, conn=conn, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            raise e

    return wrapper
