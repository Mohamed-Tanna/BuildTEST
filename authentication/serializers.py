import re
import authentication.models as models
from rest_framework import serializers
from django.core.validators import MinLengthValidator
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=30,
        validators=[MinLengthValidator(2)],
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=30,
        validators=[MinLengthValidator(2)],
    )

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.save(update_fields=["first_name", "last_name"])


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "email", "first_name", "last_name"]

        read_only_fields = ("id",)


def validate_phone_number(phone_number):
    phone_regex = r"^(\+?(1|52)[- ]?)?(\(\d{3}\)|\d{3})[- ]?\d{3}[- ]?\d{4}$"
    if not re.match(phone_regex, phone_number):
        raise serializers.ValidationError(
            "Invalid phone number. Please enter USA, Canada or Mexico phone number."
        )


class AppUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")
    phone_number = serializers.CharField(validators=[validate_phone_number])

    class Meta:
        model = models.AppUser
        fields = [
            "id",
            "user",
            "phone_number",
            "user_type",
            "selected_role",
            "username",
            "email",
            "first_name",
            "last_name",
        ]

        read_only_fields = ("id",)


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
        fields = ["app_user", "DOT_number"]


class DispatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dispatcher
        fields = ["app_user", "MC_number"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ["id", "created_by", "address", "city", "state", "zip_code", "country"]
        read_only_fields = ("id",)


class CompanySerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])

    class Meta:
        model = models.Company
        fields = ["id", "name", "EIN", "identifier", "address", "phone_number"]
        extra_kwargs = {"id": {"required": False}}
        read_only_fields = ("id",)

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
        fields = ["app_user", "TIN", "address"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["app_user"] = AppUserSerializer(instance.app_user).data
        rep["address"] = AddressSerializer(instance.address).data
        return rep

