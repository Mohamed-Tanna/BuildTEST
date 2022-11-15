from rest_framework import serializers
from .models import *


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

class LoadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Load
        fields = [
            "owner",
            "pick_up_date",
            "delivery_date",
            "pick_up_location",
            "destination",
            "status",
        ]
