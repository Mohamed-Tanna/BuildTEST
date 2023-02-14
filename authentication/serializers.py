from rest_framework import serializers
import authentication.models as models


class AppUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = models.AppUser
        fields = ["user", "phone_number", "user_type", "username", "email"]


class BaseUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name"]


class ShipmentPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShipmentParty
        fields = ["app_user"]


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Carrier
        fields = ["app_user", "DOT_number", "MC_number"]
        extra_kwargs = {"MC_number": {"required": False}}


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Broker
        fields = ["app_user", "MC_number"]
