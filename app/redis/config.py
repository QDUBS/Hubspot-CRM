import os
import redis
from dotenv import load_dotenv

load_dotenv()


class Config:
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_USERNAME = os.environ.get('REDIS_USERNAME')
    CACHE_TIMEOUT = 3600
