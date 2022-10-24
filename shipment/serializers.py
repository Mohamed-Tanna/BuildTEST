from rest_framework import exceptions, serializers

from authentication.models import ShipmentParty
from .models import Facility


class FacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = [
            "owner",
            "building_number",
            "building_name",
            "street",
            "city",
            "state",
            "zip_code",
            "country",
            "extra_info"
        ]

# class FacilityCreateSerializer(serializers.Serializer):

#     facility = FacilitySerializer()
#     # app_user = serializers.ReadOnlyField(source="app_user.id")

#     class Meta:
#         fields = ["facility"]

