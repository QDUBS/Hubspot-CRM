import requests
import time
import logging
from app.config import Config
from hubspot import HubSpot
from app.redis.redis_client import RedisClient


logger = logging.getLogger(__name__)


class HubSpotClient:
    def __init__(self, access_token=None):
        self.base_url = "https://api.hubapi.com"
        self.client_id = Config.HUBSPOT_CLIENT_ID
        self.client_secret = Config.HUBSPOT_CLIENT_SECRET
        self.refresh_token = Config.HUBSPOT_REFRESH_TOKEN
        self.access_token = access_token
        self.redis_client = RedisClient()

    def get_access_token(self):
        """Retrieve the access token from Redis or refresh if expired."""
        # Check for the token in Redis
        access_token_data = self.redis_client.get_token()

        if access_token_data:
            access_token, expires_in = access_token_data

            logger.warning(f"Token retrieved successfully.")
            if time.time() < expires_in:
                return access_token
            else:
                # If expired, refresh the token
                logger.warning(f"Token expired. Refreshing token.")
                self.refresh_access_token()
                return self.access_token
        else:
            # If token not found in Redis refresh it
            logger.warning(f"Token not found. Refreshing token.")
            self.refresh_access_token()
            return self.access_token

    def refresh_access_token(self):
        """Refresh the access token"""
        url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            data = response.json()
            new_access_token = data["access_token"]
            expires_in = data["expires_in"]

            # Store the new token and expiration time in Redis
            self.redis_client.set_token(new_access_token, expires_in)

            self.access_token = new_access_token

            logger.info(
                f"New request token generated. Status code: {response.status_code}, Response: {response.text}")
        else:
            logger.error(
                f"Token refresh failed for. Retrying token refresh.")
            raise Exception(f"Failed to refresh token: {response.text}")
