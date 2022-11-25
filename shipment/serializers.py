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
            "extra_info",
        ]
        extra_kwargs = {
            "extra_info": {"required": False},
        }


class LoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = [
            "created_by",
            "shipper",
            "consignee",
            "broker",
            "carrier",
            "pick_up_date",
            "delivery_date",
            "pick_up_location",
            "destination",
            "height",
            "width",
            "weight",
            "depth",
            "quantity",
        ]
        extra_kwargs = {
            "carrier": {"required": False},
            "broker": {"required": False},
            "quantity": {"required": False},
        }
