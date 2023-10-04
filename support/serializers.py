import os
import time
from django.db.models import Q
import support.models as models
import support.utilities as utils
from rest_framework import status
from rest_framework import serializers
from document import utilities as docs_utils
from rest_framework.response import Response
from authentication import utilities as auth_utils
from authentication.serializers import AddressSerializer

if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import GS_COMPANY_MANAGER_BUCKET_NAME
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import GS_COMPANY_MANAGER_BUCKET_NAME
else:
    from freightmonster.settings.local import GS_COMPANY_MANAGER_BUCKET_NAME


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
        fields = [
            "email",
            "first_name",
            "last_name",
            "personal_phone_number",
            "company_name",
            "company_domain",
            "company_size",
            "EIN",
            "company_fax_number",
            "company_phone_number",
            "sid_photo",
            "personal_photo",
            "address",
            "city",
            "state",
            "country",
            "zip_code",
        ]
        extra_kwargs = {
            "company_fax_number": {"required": False},
        }
        read_only_fields = ("id",)

    def create(self, validated_data):
        """
        Create a new ticket.
        """
        address = auth_utils.create_address(
            address=validated_data["address"],
            city=validated_data["city"],
            state=validated_data["state"],
            country=validated_data["country"],
            zip_code=validated_data["zip_code"],
        )
        if not address:
            return Response({"details": "Address creation failed."}, status=status.HTTP_400_BAD_REQUEST)

        del (
            validated_data["address"],
            validated_data["city"],
            validated_data["state"],
            validated_data["country"],
            validated_data["zip_code"],
        )
        validated_data["company_address"] = str(address.id)
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
        obj = models.Ticket(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            personal_phone_number=validated_data["personal_phone_number"],
            company_name=validated_data["company_name"],
            company_domain=validated_data["company_domain"],
            company_size=validated_data["company_size"],
            EIN=validated_data["EIN"],
            company_fax_number=validated_data["company_fax_number"],
            company_phone_number=validated_data["company_phone_number"],
            sid_photo=validated_data["sid_photo"],
            personal_photo=validated_data["personal_photo"],
            company_address=address,
        )
        obj.save()
        return Response(
            {"message": "Ticket created successfully"},
            status=status.HTTP_201_CREATED,
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
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "personal_phone_number",
            "company_name",
            "company_domain",
            "company_size",
            "EIN",
            "company_fax_number",
            "company_phone_number",
            "sid_photo",
            "personal_photo",
            "company_address",
            "status",
        ]
        read_only_fields = ("id",)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["sid_photo"] = docs_utils.generate_signed_url(instance.sid_photo, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME)
        representation["personal_photo"] = docs_utils.generate_signed_url(instance.personal_photo, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME)
        representation["company_address"] = AddressSerializer(instance.company_address).data
        return representation
    

