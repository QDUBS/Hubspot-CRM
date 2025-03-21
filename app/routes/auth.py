from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import logging
from ..repository.user_repository import UserRepository
from ..validations.user_validator import UserValidator
from ..validations.base import validate_request, ValidationError

# Initialize blueprint for Auth routes
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
@validate_request(UserValidator.validate_user_registration)
def register():
    data = request.get_json()
    user_repo = UserRepository()
    
    try: 
        # Check if user already exists
        existing_user = user_repo.get_user(data['username'])
        if existing_user:
            logger.warning(f"Trying to register new user with existing username: {data['username']}")
            return jsonify({'error': 'This username already exists'}), 409
        
        # Create new user
        new_user = user_repo.create(data['username'], data['password'])
        
        logger.info(f"User registered successfully: {data['username']}")
        return jsonify({'message': 'User registered successfully'}), 201
        
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@validate_request(UserValidator.validate_login)
def login():
    data = request.get_json()
    user_repo = UserRepository()
    
    try:
        # Check if user exists
        user = user_repo.get_user(data['username'])
        if not user or not user.check_password(data['password']):
            logger.warning(f"Failed login attempt for username: {data['username']}")
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token and convert user id to string
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User logged in successfully: {data['username']}")
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        logger.error(f"Error occured during user login: {str(e)}")
        return jsonify({'error': str(e)}), 500