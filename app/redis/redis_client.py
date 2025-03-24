import time
import redis
from .config import Config


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            username=Config.REDIS_USERNAME,
            ssl=True,
            decode_responses=True
        )

    def set_cache(self, key, value, timeout=Config.CACHE_TIMEOUT):
        """Store data in Redis"""
        self.client.setex(key, timeout, value)

    def get_cache(self, key):
        """Retrieve data from Redis"""
        return self.client.get(key)

    def delete_cache(self, key):
        """Delete data from Redis"""
        self.client.delete(key)

    def set_token(self, token, expires_in):
        """Store token with expiration time"""
        expiration_time = time.time() + expires_in
        token_data = {
            "token": token,
            "expiration_time": expiration_time
        }
        self.set_cache('hubspot_token', token_data)

    def get_token(self):
        """Get token from Redis."""
        token_data = self.get_cache('hubspot_token')
        if token_data:
            token_data = eval(token_data)
            if time.time() < token_data["expiration_time"]:
                return token_data["token"]
            else:
                self.delete_cache('hubspot_token')
        return None
