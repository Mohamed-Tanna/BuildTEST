import time
from django.db.models import Q
import support.models as models
import support.utilities as utils
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
import authentication.utilities as auth_utils
from authentication.serializers import AddressSerializer


class TicketSerializer(serializers.ModelSerializer):
    company_address = AddressSerializer()

    class Meta:
        model = models.Ticket
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        sid_photo = validated_data["sid_photo"]
        personal_photo = validated_data["personal_photo"]
        timestamp = int(time.time())
        
        sid_photo_name = f"sid_{timestamp}_{sid_photo.name}"
        personal_photo_name = f"personal_{timestamp}_{personal_photo.name}"

        if models.Ticket.objects.filter(
            Q(sid_photo=sid_photo_name) | Q(personal_photo=personal_photo_name)
        ).exists():
            raise serializers.ValidationError(
                {"details": "File with this name already exists."}
            )

        sid_photo.name = sid_photo_name
        personal_photo.name = personal_photo_name
        utils.upload_to_gcs(sid_photo)
        utils.upload_to_gcs(personal_photo)
        validated_data["sid_photo"] = sid_photo_name
        validated_data["personal_photo"] = personal_photo_name

        address = auth_utils.create_address(
            address=validated_data["address"],
            city=validated_data["city"],
            state=validated_data["state"],
            zip_code=validated_data["zip_code"],
            country=validated_data["country"],
        )
        if not address:
            raise serializers.ValidationError(
                {
                    "details": "Address creation failed. Please try again; if the issue persists, please contact us."
                }
            )

        del (
            validated_data["address"],
            validated_data["city"],
            validated_data["state"],
            validated_data["zip_code"],
            validated_data["country"],
        )
        validated_data["address"] = str(address.id)
        obj = models.Ticket.objects.create(**validated_data)
        obj.save()
        return Response(status=status.HTTP_201_CREATED)
