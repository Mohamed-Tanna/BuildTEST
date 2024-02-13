# Python imports
import os
import re
import time

# Django imports
from django.db.models import Q
from django.db import IntegrityError

# Third party imports
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response

# Module imports
import support.models as models
import support.utilities as utils
from authentication.models import AppUser
from document import utilities as docs_utils
from shipment.models import Claim, Load
from shipment.utilities import get_app_user_load_party_roles

if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import GS_COMPANY_MANAGER_BUCKET_NAME
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import GS_COMPANY_MANAGER_BUCKET_NAME
else:
    from freightmonster.settings.local import GS_COMPANY_MANAGER_BUCKET_NAME

ticket_fields = [
    "id",
    "email",
    "first_name",
    "last_name",
    "personal_phone_number",
    "company_name",
    "company_domain",
    "company_size",
    "EIN",
    "scac",
    "company_fax_number",
    "company_phone_number",
    "sid_photo",
    "personal_photo",
    "address",
    "city",
    "state",
    "country",
    "zip_code",
    "status",
    "insurance_provider",
    "insurance_policy_number",
    "insurance_type",
    "insurance_premium_amount",
    "created_at",
    "handled_at",
]


class CreateTicketSerializer(serializers.ModelSerializer):
    sid_photo = serializers.FileField()
    personal_photo = serializers.FileField()

    class Meta:
        model = models.Ticket
        fields = "__all__"
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'personal_phone_number': {'required': True},
            'company_name': {'required': True},
            'company_domain': {'required': True},
            'company_size': {'required': True},
            'EIN': {'required': True},
            'company_phone_number': {'required': True},
            'address': {'required': True},
            'city': {'required': True},
            'state': {'required': True},
            'zip_code': {'required': True},
            'country': {'required': True},
            'insurance_provider': {'required': True},
            'insurance_policy_number': {'required': True},
            'insurance_type': {'required': True},
            'insurance_premium_amount': {'required': True},
            'sid_photo': {'required': True},
            'personal_photo': {'required': True},
        }
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "handled_at",
            "rejection_reason"
        )

    @staticmethod
    def validate_scac(value):
        scac_validity_result = utils.is_scac_valid(value)
        if not scac_validity_result["isValid"]:
            raise serializers.ValidationError({'SCAC': scac_validity_result["message"]})
        return value

    @staticmethod
    def validate_ein(value):
        ein_validity_result = utils.ein_validation(value)
        if not ein_validity_result["isValid"]:
            raise serializers.ValidationError({'EIN': ein_validity_result["message"]})
        return value

    @staticmethod
    def validate_insurance_policy_number(value):
        IPN_validity_result = utils.min_length_validation(value, 8)
        if not IPN_validity_result["isValid"]:
            raise serializers.ValidationError({'IPN': IPN_validity_result["message"]})
        return value

    def validate(self, data):
        scac = data.get('scac', "")
        ein = data.get('EIN', None)
        insurance_policy_number = data.get('insurance_policy_number', None)
        if len(scac) > 0:
            self.validate_scac(scac)
        self.validate_ein(ein)
        self.validate_insurance_policy_number(insurance_policy_number)
        return super().validate(data)

    def create(self, validated_data):
        """
        Create a new ticket.
        """
        sid_photo = validated_data["sid_photo"]
        personal_photo = validated_data["personal_photo"]
        timestamp = int(time.time())

        sid_photo_name = f"sid_{timestamp}_{sid_photo.name}"
        personal_photo_name = f"personal_{timestamp}_{personal_photo.name}"

        sid_photo.name = sid_photo_name
        personal_photo.name = personal_photo_name
        utils.upload_to_gcs(sid_photo)
        utils.upload_to_gcs(personal_photo)
        validated_data["sid_photo"] = sid_photo_name
        validated_data["personal_photo"] = personal_photo_name
        return super().create(validated_data)


class ListTicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = [
            "id",
            "email",
            "company_name",
            "created_at",
            "status",
        ]
        read_only_fields = ("id",)


class RetrieveTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ticket_fields
        read_only_fields = ("id",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["sid_photo"] = docs_utils.generate_signed_url(
            instance.sid_photo, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME
        )
        rep["personal_photo"] = docs_utils.generate_signed_url(
            instance.personal_photo, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME
        )
        return rep


class ListClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = [
            "claimant",
            "load",
            "created_at",
            "status",
        ]
        read_only_fields = ("id",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["claimant"] = {
            "username": instance.claimant.user.username,
            "party_roles": get_app_user_load_party_roles(instance.claimant, instance.load)
        }
        representation["load"] = instance.load.name
        return representation
