from .models import *
from rest_framework import serializers
from authentication.models import AppUser


# def valid_phone_number(phone_number):
#     phone_number_pattern = re.compile(
#         "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$"
#     )
#     if not phone_number_pattern.match(phone_number):
#         raise serializers.ValidationError("invalid phone number")


class AppUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = AppUser
        fields = ["user", "phone_number", "user_type", "username"]


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
