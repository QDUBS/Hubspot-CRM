from .base import Validator, ValidationError


class SupportTicketValidator(Validator):
    # Validator for support-ticket operations

    @classmethod
    def validate_create_support_ticket(cls, data):
        # Ensure the 'properties' key exists
        if 'properties' not in data:
            raise ValidationError("Missing 'properties' in payload")

        properties = data['properties']

        # Check required fields inside 'properties'
        cls.validate_required(properties,
                              [
                                  "subject",
                                  "description",
                                  "category",
                                  "pipeline",
                                  "hs_ticket_priority",
                                  "hs_pipeline_stage",
                              ])

        # Validate subject
        cls.validate_length(properties, "subject",
                            min_length=3, max_length=500)

        # Validate description
        cls.validate_length(properties, "description",
                            min_length=3, max_length=5000)

        # Validate category
        cls.validate_length(properties, "category",
                            min_length=3, max_length=100)

        # Validate pipeline
        cls.validate_length(properties, "pipeline",
                            min_length=1, max_length=50)

        # Validate hs_ticket_priority
        cls.validate_length(properties, "hs_ticket_priority",
                            min_length=1, max_length=50)

        # Validate hs_pipeline_stagec
        cls.validate_length(properties, "hs_pipeline_stage",
                            min_length=1, max_length=50)

        return True
