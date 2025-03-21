from functools import wraps
from flask import request, jsonify
import re
import logging


class ValidationError(Exception):
    """Exception raised for validation errors"""

    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


class Validator:
    """Base validator class"""

    @staticmethod
    def validate_required(data, fields):
        """Validate that required fields are present and not empty"""
        errors = {}

        for field in fields:
            if field not in data or data[field] is None or data[field] == '':
                errors[field] = f"{field} is required"

        if errors:
            raise ValidationError(errors)

        return True

    @staticmethod
    def validate_type(data, field, expected_type, field_name=None):
        """Validate that a field is of the expected type"""
        field_name = field_name or field

        if field not in data:
            return

        value = data[field]
        if value is not None and not isinstance(value, expected_type):
            raise ValidationError(
                {field: f"{field_name} must be {expected_type.__name__}"})

        return True

    @staticmethod
    def validate_length(data, field, min_length=None, max_length=None, field_name=None):
        """Validate that a field's length is within specified bounds"""
        field_name = field_name or field

        if field not in data or data[field] is None:
            return

        value = data[field]

        # Ensure the value is a string before checking length
        if not isinstance(value, str):
            raise ValidationError({field: f"{field_name} must be a string"})

        length = len(value)

        if min_length is not None and length < min_length:
            raise ValidationError(
                {field: f"{field_name} must be at least {min_length} characters"})

        if max_length is not None and length > max_length:
            raise ValidationError(
                {field: f"{field_name} must be no more than {max_length} characters"})

        return True

    @staticmethod
    def validate_is_number(data, field_name):
        """Ensure that a field is a number."""
        if field_name not in data:
            return

        value = data.get(field_name)
        if not isinstance(value, (int, float)):
            raise ValidationError(
                {field_name: f"{field_name} must be a number."})

    @staticmethod
    def validate_email(data, field_name):
        """Basic email format check."""
        email = data.get(field_name)
        if email:
            email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if not re.match(email_regex, email):
                raise ValidationError({field_name: "Invalid email format."})

    @staticmethod
    def validate_range(data, field_name, min_value=None, max_value=None):
        """Ensure that a numeric field is within a specific range."""
        if field_name not in data:
            return

        value = data.get(field_name)

        if not isinstance(value, (int, float)):
            raise ValidationError(
                {field_name: f"{field_name} must be a number."})

        if min_value is not None and value < min_value:
            raise ValidationError(
                {field_name: f"{field_name} must be at least {min_value}"})

        if max_value is not None and value > max_value:
            raise ValidationError(
                {field_name: f"{field_name} must be no more than {max_value}"})

        return True


def validate_request(validator_method):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger = logging.getLogger(__name__)
            try:
                data = request.get_json()
                if not data:
                    logger.warning(
                        "Request validation failed: No JSON data provided")
                    return jsonify({
                        'error': 'Invalid request format',
                        'details': 'Request must contain valid JSON data'
                    }), 422

                # Apply the validator
                validator_method(data)

                return f(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"Request validation failed: {e.errors}")
                return jsonify({
                    'error': 'Validation error',
                    'details': e.errors
                }), 422

            except Exception as e:
                logger.error(f"Unexpected error during validation: {str(e)}")
                return jsonify({
                    'error': 'Invalid request',
                    'details': str(e)
                }), 400

        return decorated_function
    return decorator
