from .models import *
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import exceptions, serializers
from django.utils.translation import gettext_lazy
import re
from authentication.models import AppUser


# class CustomLoginSerializer(LoginSerializer):
#     def _validate_email(self, email, password):

#         """
#         This function is intended for the use as a custom login as it checks whether the user has completed
#         their data or not, if he did complete the required data then he will be logged in
#         if not he will get an access denied error.
#         """

#         err_msg = gettext_lazy(
#             "Insufficient user data, user must complete their account before trying to login"
#         )
#         carrier, broker, shipment_party = None, None, None
#         if email and password:
#             user = self.authenticate(email=email, password=password)
#             if user:
#                 try:
#                     app_user = AppUser.objects.get(user=user)
#                 except BaseException as e:
#                     print(f"Unexpected {e=}, {type(e)=}")
#                     msg = gettext_lazy(
#                         "Incomplete profile, please specify the user type before trying to log in"
#                     )
#                     raise exceptions.AuthenticationFailed(msg)
#                 if app_user is not None:
#                     if app_user.user_type == "carrier":
#                         try:
#                             carrier = Carrier.objects.get(app_user=app_user)
#                         except BaseException as e:
#                             print(f"Unexpected {e=}, {type(e)=}")
#                     elif app_user.user_type == "broker":
#                         try:
#                             broker = Broker.objects.get(app_user=app_user)
#                         except BaseException as e:
#                             print(f"Unexpected {e=}, {type(e)=}")
#                     elif app_user.user_type == "shipment party":
#                         try:
#                             shipment_party = ShipmentParty.objects.get(
#                                 app_user=app_user
#                             )
#                         except BaseException as e:
#                             print(f"Unexpected {e=}, {type(e)=}")

#                     if (carrier or broker or shipment_party) is None:
#                         raise exceptions.ValidationError(err_msg)
#                 return user
#             else:
#                 msg = gettext_lazy("Invalid credentials")
#                 raise exceptions.AuthenticationFailed(msg)
#         else:
#             msg = gettext_lazy('Must include "email" and "password"')
#             raise exceptions.ValidationError(msg)


def valid_phone_number(phone_number):
    phone_number_pattern = re.compile(
        "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$"
    )
    if not phone_number_pattern.match(phone_number):
        raise serializers.ValidationError("invalid phone number")


class AppUserSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(validators=[valid_phone_number])

    class Meta:
        model = AppUser
        fields = ["user", "phone_number", "user_type"]


class BaseUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class ShipmentPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentParty
        fields = ["app_user"]


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = ["app_user", "DOT_number", "MC_number"]
        extra_kwargs = {"MC_number": {"required": False}}


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ["app_user", "MC_number"]
