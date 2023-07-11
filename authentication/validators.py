import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password):
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
