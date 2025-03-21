from .base import Validator, ValidationError


class ContactValidator(Validator):
    # Validator for contact operations

    @classmethod
    def validate_registration(cls, data):

        # Ensure the 'properties' key exists
        if 'properties' not in data:
            raise ValidationError("Missing 'properties' in payload")

        properties = data['properties']

        # Check required fields inside 'properties'
        cls.validate_required(
            properties, ["email", "firstname", "lastname", "phone"])

        # Validate email
        cls.validate_length(
            data, "email", min_length=3, max_length=80
        )

        # Validate firstname
        cls.validate_length(
            data, "firstname", min_length=2, max_length=80
        )

        # Validate lastname
        cls.validate_length(
            data, "lastname", min_length=2, max_length=80
        )

        # Validate phone
        cls.validate_length(
            data, "phone", min_length=8, max_length=13
        )
        cls.validate_type(data, "phone", str, field_name="Phone")

        return True
