import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import status
from authentication.models import Company

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter.")
            )
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter.")
            )
        if not re.search(r"\d", password):
            raise ValidationError(
                _("The password must contain at least one numeric value.")
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("The password must contain at least one special character.")
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one lowercase letter, one uppercase letter, one special character, and one numeric value."
        )

def is_scac_valid(scac):
    pattern = r'^[A-Z]*$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, scac) and 2 <= len(scac) <= 4:
        companies = Company.objects.filter(scac=scac)
        if not companies.exists():
            result["isValid"] = True
        else:
            result["message"] = "scac already exists"
            result["errorStatus"] = status.HTTP_409_CONFLICT
    else:
        result["message"] = "scac length should be 2-4 characters and contain upper case letters only"
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result


def ein_validation(ein):
    pattern = r'^\d{2}-\d{7}$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, ein):
        result["isValid"] = True
    else:
        result["message"] = "Invalid EIN format. It should be in the form XX-XXXXXXX where X is a digit."
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result


def min_length_validation(value, min_length):
    pattern = fr'^[\w\d-]{{{min_length},}}$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, value):
        result["isValid"] = True
    else:
        result["message"] = (
            f"Invalid format. It should be at least {min_length} characters long and can include letters, digits, and hyphens.")
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result
