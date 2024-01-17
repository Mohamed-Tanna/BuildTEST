from rest_framework import serializers

import shipment.models as models
import shipment.utilities as utils
from authentication.serializers import AppUserSerializer, AddressSerializer
from shipment.utilities import get_app_user_load_party_roles


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Facility
        fields = [
            "id",
            "owner",
            "building_name",
            "address",
            "extra_info",
        ]
        extra_kwargs = {
            "extra_info": {"required": False},
        }
        read_only_fields = ("id",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["address"] = AddressSerializer(instance.address).data
        return rep


class ClaimCreateRetrieveSerializer(serializers.ModelSerializer):
    supporting_docs = serializers.ListField(child=serializers.FileField())

    class Meta:
        model = models.Claim
        fields = "__all__"
        extra_kwargs = {
            "description_of_loss": {"required": False},
        }
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        supporting_docs = validated_data.pop("supporting_docs", [])
        new_supporting_docs_names = utils.upload_supporting_docs(supporting_docs)
        validated_data["supporting_docs"] = new_supporting_docs_names
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        supporting_docs_info = utils.get_supporting_docs_info(instance.supporting_docs)
        representation['supporting_docs'] = supporting_docs_info
        representation['claimant'] = {
            "id": instance.claimant.id,
            "username": instance.claimant.user.username,
            "party_roles": get_app_user_load_party_roles(
                app_user=instance.claimant,
                load=instance.load
            )
        }
        return representation


class LoadListSerializer(serializers.ModelSerializer):
    has_claim = serializers.SerializerMethodField()

    class Meta:
        model = models.Load
        fields = [
            "id",
            "name",
            "customer",
            "shipper",
            "consignee",
            "dispatcher",
            "carrier",
            "pick_up_location",
            "destination",
            "pick_up_date",
            "delivery_date",
            "status",
            "has_claim"
        ]
        read_only_fields = (
            "id",
            "status",
            "has_claim"
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["customer"] = instance.customer.app_user.user.username
        rep["shipper"] = instance.shipper.app_user.user.username
        rep["consignee"] = instance.consignee.app_user.user.username
        rep["dispatcher"] = instance.dispatcher.app_user.user.username
        rep["pick_up_location"] = instance.pick_up_location.building_name
        rep["destination"] = instance.destination.building_name
        try:
            rep["carrier"] = instance.carrier.app_user.user.username
        except BaseException:
            rep["carrier"] = None
        return rep

    @staticmethod
    def get_has_claim(load):
        return models.Claim.objects.filter(load=load).exists()


class ContactListSerializer(serializers.ModelSerializer):
    contact = AppUserSerializer()

    class Meta:
        model = models.Contact
        fields = [
            "contact",
        ]


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = [
            "origin",
            "contact",
        ]


class FacilityFilterSerializer(serializers.ModelSerializer):
    city = serializers.ReadOnlyField(source=f"{models.Address.city}")
    state = serializers.ReadOnlyField(source=f"{models.Address.state}")

    class Meta:
        model = models.Facility
        fields = ["id", "building_name", "city", "state"]


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Offer
        fields = "__all__"
        extra_kwargs = {
            "status": {"required": False},
            "current": {"required": False},
        }
        read_only_fields = ("id",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["party_1"] = instance.party_1.app_user.user.username
        rep["party_2"] = instance.party_2.user.username
        return rep


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shipment
        fields = "__all__"
        read_only_fields = ("id",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["created_by"] = instance.created_by.user.username

        return rep


class LoadCreateRetrieveSerializer(serializers.ModelSerializer):
    claim = ClaimCreateRetrieveSerializer(many=False, read_only=True)

    class Meta:
        model = models.Load
        fields = "__all__"
        extra_kwargs = {
            "carrier": {"required": False},
            "quantity": {"required": False},
        }
        read_only_fields = ("id", "status", "created_at")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["created_by"] = instance.created_by.user.username
        rep["customer"] = instance.customer.app_user.user.username
        rep["shipper"] = instance.shipper.app_user.user.username
        rep["consignee"] = instance.consignee.app_user.user.username
        rep["dispatcher"] = instance.dispatcher.app_user.user.username
        try:
            rep["carrier"] = instance.carrier.app_user.user.username
        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}", "Retrieve Serial")
            rep["carrier"] = None
        rep["pick_up_location"] = {
            "id": instance.pick_up_location.id,
            "building_name": instance.pick_up_location.building_name,
            "city": instance.pick_up_location.address.city,
            "state": instance.pick_up_location.address.state,
        }
        rep["destination"] = {
            "id": instance.destination.id,
            "building_name": instance.destination.building_name,
            "city": instance.destination.address.city,
            "state": instance.destination.address.state,
        }
        rep["shipment"] = ShipmentSerializer(instance.shipment).data
        if hasattr(instance, 'claim'):
            rep['claim'] = {
                "id": ClaimCreateRetrieveSerializer(instance.claim).data.get("id")
            }
        return rep


class ShipmentAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShipmentAdmin
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["admin"] = AppUserSerializer(instance.admin).data
        rep["shipment"] = ShipmentSerializer(instance.shipment).data

        return rep


class ClaimNoteCreateRetrieveSerializer(serializers.ModelSerializer):
    supporting_docs = serializers.ListField(child=serializers.FileField(), required=False, default=list)

    class Meta:
        model = models.ClaimNote
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        supporting_docs = validated_data.pop("supporting_docs", [])
        new_supporting_docs_names = utils.upload_supporting_docs(supporting_docs)
        validated_data["supporting_docs"] = new_supporting_docs_names
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        supporting_docs_info = utils.get_supporting_docs_info(instance.supporting_docs)
        representation['supporting_docs'] = supporting_docs_info
        representation['creator'] = {
            "id": instance.creator.id,
            "username": instance.creator.user.username,
            "party_roles": get_app_user_load_party_roles(
                app_user=instance.creator,
                load=instance.claim.load
            )
        }
        return representation
