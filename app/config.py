import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # DB configuration
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')

    # HubSpot OAuth credentials
    HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
    HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
    HUBSPOT_REFRESH_TOKEN = os.getenv('HUBSPOT_REFRESH_TOKEN')

    # Remove any proxy settings that might be causing issues
    HTTP_PROXY = None
    HTTPS_PROXY = None


class DevelopmentConfig(Config):
    """ Development configuration """

    DEBUG = True


class TestingConfig(Config):
    """ Testing configuration """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)


class ProductionConfig(Config):
    """ Production configuration  """

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
