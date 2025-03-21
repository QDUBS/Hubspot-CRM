import pytest
import json
from unittest.mock import patch
from app.models import User, GeneratedText
from app import create_app


@pytest.fixture
def client():
    # Assuming you have a testing configuration
    app = create_app(config_class='testing')
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers(client):
    """Helper to get auth headers for testing authentication endpoints"""
    # Register a new user to get the authentication token
    register_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = client.post('/api/register', json=register_data)
    assert response.status_code == 201

    login_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = client.post('/api/login', json=login_data)
    assert response.status_code == 200
    access_token = json.loads(response.data)['access_token']

    return {
        'Authorization': f'Bearer {access_token}'
    }


class TestApiEndpoints:
    """Test API endpoints for Authentication and CRM Integration"""

    # --- Auth Tests ---
    def test_register(self, client):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'password': 'newpassword'
        }
        response = client.post('/api/register', json=data)

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'User registered successfully'

    def test_register_existing_user(self, client):
        """Test trying to register with an existing username"""
        data = {
            'username': 'testuser',  # Using the username created in the auth_headers fixture
            'password': 'newpassword'
        }
        response = client.post('/api/register', json=data)

        assert response.status_code == 409
        response_data = json.loads(response.data)
        assert 'error' in response_data

    def test_login(self, client):
        """Test user login"""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = client.post('/api/login', json=data)

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'access_token' in response_data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = client.post('/api/login', json=data)

        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'error' in response_data

    # --- CRM Integration Tests ---
    @patch('app.services.contact_service.ContactService.create_or_update_contact')
    def test_create_contact(self, mock_create_contact, client, auth_headers):
        """Test creating or updating a contact"""
        mock_create_contact.return_value = {
            'email': 'test@hubspot.com',
            'firstname': 'Test',
            'lastname': 'User',
            'phone': '1234567890'
        }

        data = {
            'email': 'test@hubspot.com',
            'firstname': 'Test',
            'lastname': 'User',
            'phone': '1234567890'
        }

        response = client.post(
            '/api/create_contact',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['email'] == 'test@hubspot.com'
        assert response_data['firstname'] == 'Test'

    def test_create_contact_unauthorized(self, client):
        """Test creating a contact without authorization"""
        data = {
            'email': 'test@hubspot.com',
            'firstname': 'Test',
            'lastname': 'User',
            'phone': '1234567890'
        }
        response = client.post(
            '/api/create_contact',
            json=data
        )

        assert response.status_code == 401

    @patch('app.services.deal_service.DealService.create_or_update_deal')
    def test_create_deal(self, mock_create_deal, client, auth_headers):
        """Test creating or updating a deal"""
        mock_create_deal.return_value = {
            'dealname': 'New Deal',
            'amount': 1000,
            'dealstage': 'Qualification',
            'email': 'test@hubspot.com'
        }

        data = {
            'dealname': 'New Deal',
            'amount': 1000,
            'dealstage': 'Qualification',
            'email': 'test@hubspot.com'
        }

        response = client.post(
            '/api/create_deal',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['dealname'] == 'New Deal'
        assert response_data['amount'] == 1000

    @patch('app.services.support_ticket_service.SupportTicketService.create_ticket')
    def test_create_ticket(self, mock_create_ticket, client, auth_headers):
        """Test creating a support ticket"""
        mock_create_ticket.return_value = {
            'subject': 'Issue with login',
            'description': 'User cannot log in to the system.',
            'category': 'technical_issue',
            'pipeline': 'Support',
            'hs_ticket_priority': 'high',
            'hs_pipeline_stage': 'new'
        }

        data = {
            'subject': 'Issue with login',
            'description': 'User cannot log in to the system.',
            'category': 'technical_issue',
            'pipeline': 'Support',
            'hs_ticket_priority': 'high',
            'hs_pipeline_stage': 'new'
        }

        response = client.post(
            '/api/create_ticket',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['subject'] == 'Issue with login'
        assert response_data['category'] == 'technical_issue'

    def test_create_ticket_unauthorized(self, client):
        """Test creating a support ticket without authorization"""
        data = {
            'subject': 'Issue with login',
            'description': 'User cannot log in to the system.',
            'category': 'technical_issue',
            'pipeline': 'Support',
            'hs_ticket_priority': 'high',
            'hs_pipeline_stage': 'new'
        }

        response = client.post(
            '/api/create_ticket',
            json=data
        )

        assert response.status_code == 401
