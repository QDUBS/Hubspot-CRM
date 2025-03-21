import requests
import json
import logging
from app.config import Config
from hubspot import HubSpot


logger = logging.getLogger(__name__)

class HubSpotClient:
    def __init__(self):
        self.base_url = "https://api.hubapi.com"
        self.client_id = Config.HUBSPOT_CLIENT_ID
        self.client_secret = Config.HUBSPOT_CLIENT_SECRET
        self.refresh_token = Config.HUBSPOT_REFRESH_TOKEN
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        """Retrieve the access token using the refresh token."""
        url = f"https://api.hubapi.com/oauth/v1/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            logger.info(f"Access token obtained successfully: {self.access_token[:10]}...")
            return self.access_token
        else:
            logger.error(
                f"Failed to get access token. Status code: {response.status_code}, Response: {response.text}")
            raise Exception("Unable to get access token")

    def _make_request(self, method, url, data=None):
        """Helper method to make authenticated API requests."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(
                url, headers=headers, data=json.dumps(data))

        if response.status_code == 401:
            # Log the failed API request and authentication issue
            logger.warning(
                f"API Authentication failed for URL: {url}. Retrying token refresh.")

            # Token expired, refresh it
            self.access_token = self._get_access_token()
            return self._make_request(method, url, data)
        
        if response.status_code != 200:
            # Log any other error responses to help with debugging
            logger.error(
                f"API Request failed for URL: {url}. Status code: {response.status_code}, Response: {response.text}")

        return response

    def check_and_refresh_token(self):
        """Check if the token is valid; refresh if necessary."""
        if not self.access_token:
            self.access_token = self._get_access_token()
