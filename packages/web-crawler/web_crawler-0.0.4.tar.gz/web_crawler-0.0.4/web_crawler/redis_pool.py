import redis

from web_crawler.config import Config


class RedisPool(object):

    def __init__(self):
        self.connection = self._init_connection()

    def _init_connection(self):
        conn = redis.StrictRedis(
                    host=Config.REDIS_RESULTS_HOST,
                    port=Config.REDIS_RESULTS_PORT,
                    db=0
                )
        return conn

    def set(self, key, value):
        self.connection.set(key, value)

    def get(self, key):
        return self.connection.get(key)
