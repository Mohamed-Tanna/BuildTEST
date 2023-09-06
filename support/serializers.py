from rest_framework import serializers
import support.models as models
from authentication.serializers import AddressSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import authentication.models as auth_models
import shipment.models as ship_models
import document.utilities as docs_utils


class TicketSerializer(serializers.ModelSerializer):
    company_address = AddressSerializer()

    class Meta:
        model = models.Ticket
        fields = "__all__"
        read_only_fields = (
            "id",
        )
    
    def create(self, validated_data):
        sid_photo = validated_data["sid_photo"]
        personal_photo = validated_data["personal_photo"]
        
