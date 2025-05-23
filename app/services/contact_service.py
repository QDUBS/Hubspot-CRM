from hubspot import HubSpot
from hubspot.crm.contacts import ApiException
from app.services import HubSpotClient
from app.redis.redis_client import RedisClient
from app.config import Config
import time
import json
import logging

logger = logging.getLogger(__name__)
redis_client = RedisClient()

class ContactService(HubSpotClient):
    def __init__(self):
        # Initialize with OAuth access token
        super().__init__()
        access_token = self.get_access_token()
        self.client = HubSpot(access_token=access_token)

    def create_or_update_contact(self, data):
        """Create or update a contact."""
        email = data['properties']['email']

        contact_exists = self._get_contact_by_email(email)

        if contact_exists:
            # If contact exists, update
            logger.info(
                f"Contact with email {email} exists. Updating contact.")

            return self._update_contact(contact_exists.id, data)
        else:
            # If contact does not exist, create a new one
            logger.info(
                f"Contact with email {email} does not exist. Creating a new contact.")
            return self._create_contact(data)

    def _get_contact_by_email(self, email):
        """Check if the contact exists by email and return the contact if found."""
        try:
            # Search API to find a contact by email
            filter = {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }
                ]
            }
            response = self.client.crm.contacts.search_api.do_search(filter)
            if response.results:
                # Return the first result
                contact = response.results[0]
                return contact
            return None
        except ApiException as e:
            logger.error(
                f"Error fetching contact by email {email}. Status code: {e.status}, Response: {e.body}")
            return None

    def _create_contact(self, data):
        """Create a new contact."""
        contact_data = {
            "properties": {
                "email": data['properties']['email'],
                "firstname": data['properties'].get('firstname'),
                "lastname": data['properties'].get('lastname'),
                "phone": data['properties'].get('phone')
            }
        }
        try:
            # Create a contact
            response = self.client.crm.contacts.basic_api.create(contact_data)
            logger.info(
                f"Successfully created contact with email {data['properties']['email']}")
            return response
        except ApiException as e:
            logger.error(
                f"Failed to create contact. Status code: {e.status}, Response: {e.body}")
            raise

    def _update_contact(self, contact_id, data):
        """Update an existing contact."""
        contact_data = {
            "properties": {
                "email": data['properties']['email'],
                "firstname": data['properties']['firstname'],
                "lastname": data['properties']['lastname'],
                "phone": data['properties']['phone']
            }
        }
        try:
            # Update the contact
            response = self.client.crm.contacts.basic_api.update(
                contact_id, contact_data)
            logger.info(
                f"Successfully updated contact with email {data['properties']['email']}")
            return response.to_dict()
        except ApiException as e:
            logger.error(
                f"Failed to update contact. Status code: {e.status}, Response: {e.body}")
            raise

    def get_recent_contacts(self, page, page_size):
        """Retrieve recently created contacts with Redis caching."""
        cache_key = f"contacts_page_{page}_size_{page_size}"
        cached_data = redis_client.get_cache(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # If not cached fetch from HubSpot and cache the result
        try:
            response = self.client.crm.contacts.basic_api.get_page(
                limit=page_size, after=page * page_size)
            contacts = response.results

            # Cache the response
            redis_client.set_cache(cache_key, json.dumps(contacts))

            return contacts
        except ApiException as e:
            logger.error(
                f"Error fetching recent contacts. Status code: {e.status}, Response: {e.body}")
            return []

    def handle_rate_limit(self, response):
        """Handle rate limits using exponential backoff."""
        retries = 3

        if response.status_code == 429:
            # Get retry-after time from headers
            retry_after = int(response.headers.get("Retry-After", 1))
            wait_time = retry_after * (2 ** retries)
            logger.warning(
                f"Rate limit exceeded. Retrying after {wait_time} seconds.")
            time.sleep(retry_after)

            # Retry after waiting
            return True
        return False
