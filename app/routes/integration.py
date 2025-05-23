from flask import Blueprint, request, jsonify
import logging
from app.services.contact_service import ContactService
from app.services.deal_service import DealService
from app.services.support_ticket_service import SupportTicketService
from ..middleware.auth import auth_middleware
from ..validations.contact_validator import ContactValidator
from ..validations.deal_validator import DealValidator
from ..validations.support_ticket_validator import SupportTicketValidator
from ..validations.base import validate_request

# Initialize blueprint for Integration routes
integration_bp = Blueprint('integration_bp', __name__)
logger = logging.getLogger(__name__)

# Instantiate services 
contact_service = ContactService() 
deal_service = DealService()
ticket_service = SupportTicketService()


@integration_bp.route('/create_contact', methods=['POST'])
@auth_middleware()
@validate_request(ContactValidator.validate_registration)
def create_or_update_contact():
    data = request.get_json()

    try:
        contact = contact_service.create_or_update_contact(data)
        return jsonify(contact), 200
    except ValueError as e:
        logger.error(f"Error processing contact: {e}")
        return jsonify({"Error": str(e)}), 400


@integration_bp.route('/create_deal', methods=['POST'])
@auth_middleware()
@validate_request(DealValidator.validate_create_deal)
def create_or_update_deal():
    data = request.get_json()

    try:
        deal = deal_service.create_or_update_deal(data)
        return jsonify(deal), 200
    except ValueError as e:
        logger.error(f"Error processing deal: {e}")
        return jsonify({"Error": str(e)}), 400


@integration_bp.route('/create_ticket', methods=['POST'])
@auth_middleware()
@validate_request(SupportTicketValidator.validate_create_support_ticket)
def create_ticket():
    data = request.get_json()

    try:
        ticket = ticket_service.create_ticket(data)
        return jsonify(ticket), 200
    except ValueError as e:
        logger.error(f"Error processing ticket: {e}")
        return jsonify({"Error": str(e)}), 400


@integration_bp.route('/new_crm_objects', methods=['GET'])
@auth_middleware()
def get_new_crm_objects():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    sort_by = request.args.get('sort_by', 'id')  # Default sort by 'id'
    filter_by = request.args.get('filter_by', '')  # No default filter

    try:
        contacts = contact_service.get_recent_contacts(page, page_size)
        deals = deal_service.get_recent_deals(page, page_size)
        tickets = ticket_service.get_recent_tickets(page, page_size)

        # Sort dynamically based on query parameter
        if sort_by:
            contacts.sort(key=lambda x: x.get(sort_by))
            deals.sort(key=lambda x: x.get(sort_by))
            tickets.sort(key=lambda x: x.get(sort_by))

        # Apply filtering if requested
        if filter_by:
            contacts = [c for c in contacts if filter_by.lower()
                        in str(c).lower()]
            deals = [d for d in deals if filter_by.lower() in str(d).lower()]
            tickets = [t for t in tickets if filter_by.lower()
                       in str(t).lower()]

        # Return the results in an object
        crm_objects = {
            "contacts": [contact.to_dict() for contact in contacts],
            "deals": [deal.to_dict() for deal in deals],
            "tickets": [ticket.to_dict() for ticket in tickets],
        }

        return jsonify(crm_objects), 200
    except ValueError as e:
        logger.error(f"Error retrieving new CRM objects: {e}")
        return jsonify({"Error": str(e)}), 400
