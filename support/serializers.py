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


class CreateTicketSerializer(serializers.Serializer):
    sid_photo = serializers.FileField()
    personal_photo = serializers.FileField()
    city = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=255)
    zip_code = serializers.CharField(max_length=255)

    class Meta:
        model = models.Ticket
        fields = ticket_fields
        extra_kwargs = {
            "company_fax_number": {"required": False},
            "scac": {"required": False},
        }
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "handled_at",
        )

    def create(self, validated_data):
        """
        Create a new ticket.
        """
        sid_photo = validated_data["sid_photo"]
        personal_photo = validated_data["personal_photo"]
        timestamp = int(time.time())

        sid_photo_name = f"sid_{timestamp}_{sid_photo.name}"
        personal_photo_name = f"personal_{timestamp}_{personal_photo.name}"

        if models.Ticket.objects.filter(
                Q(sid_photo=sid_photo_name) | Q(personal_photo=personal_photo_name)
        ).exists():
            return Response(
                {"message": "The photo already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        sid_photo.name = sid_photo_name
        personal_photo.name = personal_photo_name
        utils.upload_to_gcs(sid_photo)
        utils.upload_to_gcs(personal_photo)
        validated_data["sid_photo"] = sid_photo_name
        validated_data["personal_photo"] = personal_photo_name
        company_fax_number = ""
        scac = ""
        if "company_fax_number" in validated_data:
            company_fax_number = validated_data["company_fax_number"]
        if "scac" in validated_data:
            scac = validated_data["scac"].strip()
        if len(scac) > 0:
            scac_validity_result = utils.is_scac_valid(scac)
            if not scac_validity_result["isValid"]:
                return Response(
                    {"SCAC": scac_validity_result["message"]},
                    status=scac_validity_result["errorStatus"],
                )
        if "EIN" in validated_data:
            ein_validity_result = utils.ein_validation(validated_data["EIN"])
            if not ein_validity_result["isValid"]:
                return Response(
                    {"EIN": ein_validity_result["message"]},
                    status=ein_validity_result["errorStatus"],
                )
        if "insurance_policy_number" in validated_data:
            IPN_validity_result = utils.min_length_validation(validated_data["insurance_policy_number"], 8)
            if not IPN_validity_result["isValid"]:
                return Response(
                    {"IPN": IPN_validity_result["message"]},
                    status=IPN_validity_result["errorStatus"],
                )

        obj = models.Ticket(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            personal_phone_number=validated_data["personal_phone_number"],
            company_name=validated_data["company_name"],
            company_domain=validated_data["company_domain"],
            company_size=validated_data["company_size"],
            EIN=validated_data["EIN"],
            scac=scac,
            company_fax_number=company_fax_number,
            company_phone_number=validated_data["company_phone_number"],
            sid_photo=validated_data["sid_photo"],
            personal_photo=validated_data["personal_photo"],
            address=validated_data["address"],
            city=validated_data["city"],
            state=validated_data["state"],
            country=validated_data["country"],
            zip_code=validated_data["zip_code"],
            insurance_provider=validated_data["insurance_provider"],
            insurance_policy_number=validated_data["insurance_policy_number"],
            insurance_type=validated_data["insurance_type"],
            insurance_premium_amount=validated_data["insurance_premium_amount"],
        )
        try:
            obj.save()
            return Response(
                {"details": "Ticket created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError as e:
            error_message = str(e)
            match = re.search(r"Key \((.*?)\)=\((.*?)\) already exists", error_message)
            if match:
                refined_column_name = match.group(1).replace("_", "").title()
                return Response(
                    {refined_column_name: f'This {refined_column_name} already exists.'},
                    status=status.HTTP_409_CONFLICT,
                )
        except Exception as e:
            return Response(
                {"details": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
