from rest_framework import serializers
from .models import *
from authentication.serializers import AppUserSerializer


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = [
            "id",
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
        read_only_fields = ("id",)


class LoadCreateRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = "__all__"
        extra_kwargs = {
            "carrier": {"required": False},
            "broker": {"required": False},
            "quantity": {"required": False},
        }
        read_only_fields = (
            "id",
            "status",
        )


class LoadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = [
            "id",
            "name",
            "shipper",
            "consignee",
            "broker",
            "pick_up_location",
            "destination",
            "pick_up_date",
            "delivery_date",
            "status",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["shipper"] = instance.shipper.app_user.user.username
        rep["consignee"] = instance.consignee.app_user.user.username
        try:
            rep["broker"] = instance.broker.app_user.user.username
        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            rep["broker"] = None
        rep["pick_up_location"] = instance.pick_up_location.building_name
        rep["destination"] = instance.destination.building_name
        return rep


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
        fields = ["id", "building_name", "state", "city"]
