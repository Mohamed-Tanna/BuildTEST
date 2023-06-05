# Python imports
import string, random

# Django imports
from django.db import IntegrityError

# Third party imports
from allauth.account.utils import user_field
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):

        """
        Changing the confirmation URL to fit the domain that we are working on
        """

        url = "https://dev.freightslayer.com/verify/" + emailconfirmation.key
        return url

    def save_user(self, request, user, form, commit=False):

        """
        Custom function to override the save_user() which allows a custom user registeration
        """

        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        email = data.get("email")
        if first_name:
            user_field(user, "first_name", first_name)
        if last_name:
            user_field(user, "last_name", last_name)

        username = email.split("@")[0]

        modified_username = (
            username
            + "#"
            + (
                "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(5)
                )
            )
        )
        user.username = modified_username

        while True:
            try:
                user.save()
                break

            except IntegrityError:
                username = data["username"].split("#")[0]
                modified_username = (
                    username
                    + "#"
                    + (
                        "".join(
                            random.choice(string.ascii_uppercase + string.digits)
                            for _ in range(5)
                        )
                    )
                )
                user.username = modified_username
                continue

            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                break

        return user
