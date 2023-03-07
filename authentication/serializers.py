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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ["building_number", "street", "city", "state", "zip_code", "country"]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ["name", "EIN", "identifier", "address"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["address"] = AddressSerializer(instance.address).data
        return rep


class CompanyEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyEmployee
        fields = ["app_user", "company"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["app_user"] = AppUserSerializer(instance.app_user).data
        rep["company"] = CompanySerializer(instance.company).data
        return rep


class UserTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserTax
        fields = ["app_user", "TIN"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["app_user"] = AppUserSerializer(instance.app_user).data
        return rep
