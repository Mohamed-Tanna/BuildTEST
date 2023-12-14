import shipment.models as models
from rest_framework import serializers
from authentication.serializers import AppUserSerializer, AddressSerializer


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


class LoadListSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = (
            "id",
            "status",
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
        except (BaseException):
            rep["carrier"] = None
        return rep


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


class ClaimedOnSerializer(serializers.ModelSerializer):
    claimed_on_parties = serializers.SerializerMethodField()

    class Meta:
        model = models.Load
        fields = ['claimed_on_parties']

    def get_claimed_on_parties(self, load):
        result = []
        app_user_id = self.context.get('app_user_id')
        load_customer = load.customer
        load_shipper = load.shipper
        load_dispatcher = load.dispatcher
        load_carrier = load.carrier
        load_consignee = load.consignee
        if load_customer.app_user.id != app_user_id:
            result.append(
                {
                    "id": load_customer.app_user.user.id,
                    "name": load_customer.app_user.user.username,
                    "party_role": "customer"
                }
            )
        if load_shipper.app_user.id != app_user_id:
            result.append(
                {
                    "id": load_shipper.app_user.user.id,
                    "name": load_shipper.app_user.user.username,
                    "party_role": "shipper"
                }
            )
        if load_dispatcher.app_user.id != app_user_id:
            result.append(
                {
                    "id": load_dispatcher.app_user.user.id,
                    "name": load_dispatcher.app_user.user.username,
                    "party_role": "dispatcher"
                }
            )
        if load_carrier.app_user.id != app_user_id:
            result.append(
                {
                    "id": load_carrier.app_user.user.id,
                    "name": load_carrier.app_user.user.username,
                    "party_role": "carrier"
                }
            )
        if load_consignee.app_user.id != app_user_id:
            result.append(
                {
                    "id": load_consignee.app_user.user.id,
                    "name": load_consignee.app_user.user.username,
                    "party_role": "consignee"
                }
            )
        return result
