import re

from django.core.exceptions import ValidationError


def validate_georgian_personal_id(value):
    """Validate Georgian personal ID number (11 digits)."""
    if not re.match(r"^\d{11}$", str(value)):
        raise ValidationError(
            "Personal ID must be exactly 11 digits.",
            code="invalid_personal_id",
        )


def validate_georgian_phone(value):
    """Validate Georgian phone number format (+995XXXXXXXXX)."""
    if not re.match(r"^\+995\d{9}$", str(value)):
        raise ValidationError(
            "Phone number must be in format +995XXXXXXXXX.",
            code="invalid_phone",
        )
