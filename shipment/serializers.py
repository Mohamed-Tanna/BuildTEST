from rest_framework import serializers
from .models import *
from authentication.serializers import AppUserSerializer


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
            "name",
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


class ContactListSerializer(serializers.ModelSerializer):
    contact = AppUserSerializer()

    class Meta:
        model = Contact
        fields = [
            "contact",
        ]


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "origin",
            "contact",
        ]


class FacilityFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ["building_name", "state", "city"]