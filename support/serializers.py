from rest_framework import serializers
import support.models as models
from authentication.serializers import AddressSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import authentication.utilities as create_address
import support.utilities as utils


class TicketSerializer(serializers.ModelSerializer):
    company_address = AddressSerializer()

    class Meta:
        model = models.Ticket
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        sid_photo = validated_data["sid_photo"]
        personal_photo = validated_data["personal_photo"]
        name = validated_data["first_name"].strip() + " " + validated_data["last_name"]
        sid_photo_name = "sid" + "_" + name + "_" + sid_photo.name
        personal_photo_name = "personal" + "_" + name + "_" + personal_photo.name
        sid_conflict = models.Ticket.objects.filter(sid_photo=sid_photo_name).exists()
        personal_conflict = models.Ticket.objects.filter(personal_photo=personal_photo_name).exists()
        if sid_conflict or personal_conflict:
            return Response(
                    [{"details": "File with this name already exists."}],
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            sid_photo.name = sid_photo_name
            personal_photo.name = personal_photo_name
            utils.upload_to_gcs(sid_photo)
            utils.upload_to_gcs(personal_photo)
            validated_data["sid_photo"] = sid_photo_name
            validated_data["personal_photo"] = personal_photo_name


