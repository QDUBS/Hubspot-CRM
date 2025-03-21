from .base import Validator, ValidationError


class DealValidator(Validator):
    # Validator for deal operations

    @classmethod
    def validate_create_deal(cls, data):
        # Ensure the 'properties' key exists
        if 'properties' not in data:
            raise ValidationError("Missing 'properties' in payload")

        properties = data['properties']

        # Check required fields inside 'properties'
        cls.validate_required(
            properties, ["dealname", "amount", "dealstage", "contact_id", "pipeline"])

        # Validate dealname
        cls.validate_length(data, "dealname", min_length=3, max_length=5000)

        # Validate amount (should be a valid number)
        cls.validate_is_number(data, "amount")

        # Optional: Ensure amount is not negative
        cls.validate_range(data, "amount", min_value=0)

        # Validate dealstage
        cls.validate_length(data, "dealstage", min_length=3, max_length=5000)

        # Validate contact_id
        cls.validate_length(data, "contact_id", min_length=3, max_length=5000)

        # Validate pipeline
        cls.validate_length(data, "pipeline", min_length=3, max_length=5000)

        return True
