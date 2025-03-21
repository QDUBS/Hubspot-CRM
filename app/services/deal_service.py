from hubspot import HubSpot
from hubspot.crm.deals import ApiException
from app.services import HubSpotClient
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class DealService(HubSpotClient):
    def __init__(self):
        # Initialize HubSpot client with OAuth access token
        super().__init__()
        self.client = HubSpot(access_token=self.access_token)

    def create_or_update_deal(self, data):
        """Create or update a deal in HubSpot."""
        deal_name = data['properties']['dealname']
        existing_deals = self.search_deals(deal_name)

        if existing_deals:
            # If deal exists, update
            logger.info(f"Deal with name {deal_name} exists. Updating deal.")
            deal_id = existing_deals.id
            return self._update_deal(deal_id, data)
        else:
            # If no deal exists, create new one
            logger.info(
                f"Deal with name {deal_name} does not exist. Creating a new deal.")
            return self._create_deal(data)

    def _create_deal(self, data):
        """Create a new deal in HubSpot."""
        deal_data = {
            "properties": {
                "dealname": data['properties']['dealname'],
                "amount": data['properties'].get('amount'),
                "dealstage": data['properties'].get('dealstage'),
                "contact_id": data['properties'].get('contact_id'),
            }
        }

        try:
            response = self.client.crm.deals.basic_api.create(deal_data)
            logger.info(
                f"Successfully created deal with name {data['properties']['dealname']}")
            return response.to_dict()
        except ApiException as e:
            logger.error(
                f"Failed to create deal. Status code: {e.status}, Response: {e.body}")
            raise

    def _update_deal(self, deal_id, data):
        print(
            "\nAbout to update deal\n",
            data
        )

        """Update an existing deal in HubSpot."""
        deal_data = {
            "properties": {
                "dealname": data['properties']['dealname'],
                "amount": data['properties'].get('amount'),
                "dealstage": data['properties'].get('dealstage'),
                "contact_id": data['properties'].get('contact_id'),
            }
        }
        try:
            response = self.client.crm.deals.basic_api.update(
                deal_id, deal_data)
            logger.info(
                f"Successfully updated deal with name {data['properties']['dealname']}")
            return response.to_dict()
        except ApiException as e:
            logger.error(
                f"Failed to update deal. Status code: {e.status}, Response: {e.body}")
            raise

    def search_deals(self, deal_name):
        """Search API to find an existing deal by name."""
        try:
            filter = {
                "filters": [
                    {
                        "propertyName": "dealname",
                        "operator": "EQ",
                        "value": deal_name
                    }
                ]
            }
            response = self.client.crm.deals.search_api.do_search(filter)
            if response.results:
                # Return the first result
                deal = response.results[0]
                return deal
            return None
        except ApiException as e:
            logger.error(
                f"Error fetching deal with name {deal_name}. Status code: {e.status}, Response: {e.body}")
            return None

    def get_recent_deals(self, page, page_size):
        """Retrieve recently created deals."""
        try:
            response = self.client.crm.deals.basic_api.get_page(
                limit=page_size, after=page * page_size)
            return response.results
        except ApiException as e:
            logger.error(
                f"Error fetching recent deals. Status code: {e.status}, Response: {e.body}")
            return []
