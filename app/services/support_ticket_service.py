from hubspot import HubSpot
from hubspot.crm.tickets import ApiException
from app.services import HubSpotClient
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class SupportTicketService(HubSpotClient):
    def __init__(self):
        # Initialize HubSpot client with OAuth access token
        super().__init__()
        self.client = HubSpot(access_token=self.access_token)

    def create_ticket(self, data):
        """Create a new support ticket in HubSpot."""
        ticket_data = {
            "properties": {
                "subject": data['properties'].get("subject"),
                "description": data['properties'].get("description"),
                "category": data['properties'].get("category"),
                "pipeline": data['properties'].get("pipeline"),
                "hs_ticket_priority": data['properties'].get("hs_ticket_priority"),
                "hs_pipeline_stage": data['properties'].get("hs_pipeline_stage"),
            },
            "associations": []
        }

        # Create association for contact
        if "contact_id" in data['properties']:
            ticket_data["associations"].append({
                "to": {
                    "id": data['properties'].get("contact_id")
                },
                "types": [
                    {
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 16  # 16 represents "Ticket to Contact" in HubSpot
                    }
                ]
            })

        # Create associations for deals
        if "deal_ids" in data['properties']:
            # If 'deal_ids' is a string, split into list (if it's not already)
            deal_ids = data['properties'].get("deal_ids")
            if isinstance(deal_ids, str):
                deal_ids = [deal_ids]

            for deal_id in deal_ids:
                ticket_data["associations"].append({
                    "to": {
                        "id": deal_id
                    },
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 26  # 26 represents "Ticket to Deal" in HubSpot
                        }
                    ]
                })


        try:
            response = self.client.crm.tickets.basic_api.create(ticket_data)
            logger.info(f"Ticket created successfully: {response}")
            return response.to_dict()
        except ApiException as e:
            logger.error(
                f"Failed to create ticket: {e.status}, Response: {e.body}")
            return {"error": "Ticket creation failed", "status_code": e.status, "response": e.body}


    def get_recent_tickets(self, page, page_size):
        """Retrieve recently created tickets."""
        try:
            response = self.client.crm.tickets.basic_api.get_page(
                limit=page_size, after=page * page_size)
            return response.results
        except ApiException as e:
            logger.error(
                f"Error fetching recent tickets. Status code: {e.status}, Response: {e.body}")
            return []
