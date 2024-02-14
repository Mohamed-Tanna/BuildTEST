from rest_framework import serializers

import shipment.models as models
import shipment.utilities as utils
from authentication.models import AppUser, ShipmentParty
from authentication.serializers import AppUserSerializer, AddressSerializer
from freightmonster.classes import StorageClient
from freightmonster.constants import GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME, LOAD_NOTES_FILES_PATH, \
    CLAIM_NOTES_FILES_PATH, CLAIM_FILES_PATH
from shipment.utilities import get_app_user_load_party_roles
import rest_framework.exceptions as exceptions


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
        read_only_fields = ("id", "created_at", "updated_at")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["address"] = AddressSerializer(instance.address).data
        return rep

    def update(self, instance, validated_data):
        if "owner" in validated_data:
            del validated_data["owner"]
        address_serializer = AddressSerializer(
            instance.address,
            data=self.context["address"],
            partial=True
        )
        address_serializer.is_valid(raise_exception=True)
        address_serializer.save()
        return super().update(instance, validated_data)


class ClaimCreateRetrieveSerializer(serializers.ModelSerializer):
    storage_client = StorageClient().storage_client
    bucket = storage_client.get_bucket(GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME)
    blob_path = CLAIM_FILES_PATH

    class Meta:
        model = models.Claim
        fields = "__all__"
        extra_kwargs = {
            "description_of_loss": {"required": False},
            "supporting_docs": {"required": False},
        }
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        supporting_docs_names = validated_data.get("supporting_docs", [])
        new_supporting_docs_names = []

        for supporting_doc_name in supporting_docs_names:
            new_unique_supporting_doc_name = utils.generate_new_unique_file_name(
                file_name=supporting_doc_name,
            )
            blob = self.bucket.blob(f"{self.blob_path}{new_unique_supporting_doc_name}")
            if blob.exists() or new_unique_supporting_doc_name in new_supporting_docs_names:
                blob = utils.get_unique_blob(
                    bucket=self.bucket,
                    file_name=supporting_doc_name,
                    list_of_names_to_compare=new_supporting_docs_names,
                    path_name=self.blob_path
                )
            new_supporting_docs_names.append(blob.name.replace(self.blob_path, "").strip())
        validated_data["supporting_docs"] = new_supporting_docs_names
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
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
        if request and request.method == 'POST':
            supporting_docs_content_type = self.context.get('supporting_docs_content_type')
            signed_urls = []
            content_types = []
            for i in range(len(representation["supporting_docs"])):
                supporting_doc_name = representation["supporting_docs"][i]
                blob = self.bucket.blob(f"{self.blob_path}{supporting_doc_name}")
                url = utils.generate_put_signed_url_for_file(
                    blob=blob,
                    content_type=supporting_docs_content_type[i],
                    storage_client=self.storage_client,
                    headers={
                        "x-goog-meta-claim_id": f'{instance.id}'
                    }
                )
                content_types.append(supporting_docs_content_type[i])
                signed_urls.append(url)
            for i in range(len(supporting_docs_info)):
                supporting_docs_info[i]["url"] = signed_urls[i]
                supporting_docs_info[i]["content_type"] = content_types[i]
        else:
            for i in range(len(representation["supporting_docs"])):
                supporting_doc_name = representation["supporting_docs"][i]
                blob = self.bucket.blob(f"{self.blob_path}{supporting_doc_name}")
                url = ""
                content_type = ""
                if blob.exists():
                    url = utils.generate_get_signed_url_for_file(
                        blob=blob,
                        storage_client=self.storage_client,
                    )
                    blob.reload()
                    content_type = blob.content_type
                supporting_docs_info[i]["url"] = url
                supporting_docs_info[i]["content_type"] = content_type
        representation["supporting_docs"] = supporting_docs_info

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
            'created_by': {'required': True},
            'customer': {'required': True},
            'shipper': {'required': True},
            'consignee': {'required': True},
            'dispatcher': {'required': True},
            'pick_up_date': {'required': True},
            'delivery_date': {'required': True},
            'pick_up_location': {'required': True},
            'destination': {'required': True},
            'length': {'required': True},
            'width': {'required': True},
            'height': {'required': True},
            'weight': {'required': True},
            'commodity': {'required': True},
            'goods_info': {'required': True},
            'load_type': {'required': True},
            'status': {'required': True},
            'shipment': {'required': True},
        }
        read_only_fields = ("id", "status", "created_at")

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if self.context['request'].method in ['PATCH']:
            extra_kwargs['name'] = {'required': False}
            extra_kwargs['created_by'] = {'required': False}
        return extra_kwargs

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
    storage_client = StorageClient().storage_client
    bucket = storage_client.get_bucket(GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME)
    blob_path = CLAIM_NOTES_FILES_PATH

    class Meta:
        model = models.ClaimNote
        fields = "__all__"
        extra_kwargs = {
            "supporting_docs": {"required": False},
        }
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        supporting_docs_names = validated_data.get("supporting_docs", [])
        new_supporting_docs_names = []

        for supporting_doc_name in supporting_docs_names:
            new_unique_supporting_doc_name = utils.generate_new_unique_file_name(
                file_name=supporting_doc_name,
            )
            blob = self.bucket.blob(f"{self.blob_path}{new_unique_supporting_doc_name}")
            if blob.exists() or new_unique_supporting_doc_name in new_supporting_docs_names:
                blob = utils.get_unique_blob(
                    bucket=self.bucket,
                    file_name=supporting_doc_name,
                    list_of_names_to_compare=new_supporting_docs_names,
                    path_name=self.blob_path
                )
            new_supporting_docs_names.append(blob.name.replace(self.blob_path, "").strip())
        validated_data["supporting_docs"] = new_supporting_docs_names
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['creator'] = {
            "id": instance.creator.id,
            "username": instance.creator.user.username,
            "party_roles": get_app_user_load_party_roles(
                app_user=instance.creator,
                load=instance.claim.load
            )
        }
        supporting_docs_info = []
        for supporting_doc_name in representation["supporting_docs"]:
            supporting_docs_info.append(
                {
                    "name": supporting_doc_name,
                    "url": ""
                }
            )
        if request and request.method == 'POST':
            supporting_docs_content_type = self.context.get('supporting_docs_content_type')
            signed_urls = []
            content_types = []
            for i in range(len(representation["supporting_docs"])):
                supporting_doc_name = representation["supporting_docs"][i]
                blob = self.bucket.blob(f"{self.blob_path}{supporting_doc_name}")
                url = utils.generate_put_signed_url_for_file(
                    blob=blob,
                    content_type=supporting_docs_content_type[i],
                    storage_client=self.storage_client,
                    headers={
                        "x-goog-meta-claim_note_id": f'{instance.id}'
                    }
                )
                content_types.append(supporting_docs_content_type[i])
                signed_urls.append(url)
            for i in range(len(supporting_docs_info)):
                supporting_docs_info[i]["url"] = signed_urls[i]
                supporting_docs_info[i]["content_type"] = content_types[i]
        else:
            for i in range(len(representation["supporting_docs"])):
                supporting_doc_name = representation["supporting_docs"][i]
                blob = self.bucket.blob(f"{self.blob_path}{supporting_doc_name}")
                url = ""
                content_type = ""
                if blob.exists():
                    url = utils.generate_get_signed_url_for_file(
                        blob=blob,
                        storage_client=self.storage_client,
                    )
                    blob.reload()
                    content_type = blob.content_type
                supporting_docs_info[i]["url"] = url
                supporting_docs_info[i]["content_type"] = content_type
        representation["supporting_docs"] = supporting_docs_info
        return representation


class OtherLoadPartiesSerializer(serializers.ModelSerializer):
    other_load_parties = serializers.SerializerMethodField()

    class Meta:
        model = models.Load
        fields = ['other_load_parties']

    @staticmethod
    def merge_same_parties_with_different_roles(list_of_parties):
        merged_parties = {}
        for party in list_of_parties:
            party_id = party["id"]
            if party_id not in merged_parties:
                merged_parties[party_id] = {
                    "id": party_id,
                    "username": party["username"],
                    "party_roles": [party["party_roles"][0]]
                }
            else:
                merged_parties[party_id]["party_roles"].append(party["party_roles"][0])
        return list(merged_parties.values())

    def get_other_load_parties(self, load):
        result = []
        app_user_id = self.context.get('app_user_id')
        party_roles = {
            "customer": load.customer,
            "shipper": load.shipper,
            "dispatcher": load.dispatcher,
            "carrier": load.carrier,
            "consignee": load.consignee
        }
        for role, party in party_roles.items():
            if party is not None and party.app_user.id != app_user_id:
                result.append(
                    {
                        "id": party.app_user.id,
                        "username": party.app_user.user.username,
                        "party_roles": [role]
                    }
                )
        return self.merge_same_parties_with_different_roles(result)


class LoadNoteSerializer(serializers.ModelSerializer):
    storage_client = StorageClient().storage_client
    bucket = storage_client.get_bucket(GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME)
    blob_path = LOAD_NOTES_FILES_PATH
    visible_to = serializers.PrimaryKeyRelatedField(
        queryset=AppUser.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = models.LoadNote
        fields = '__all__'
        extra_kwargs = {
            "attachments": {"required": False},
            "is_deleted": {"required": False},
        }
        read_only_fields = ("id", "created_at", "is_deleted", "updated_at")

    def create(self, validated_data):
        attachments_names = validated_data.get("attachments", [])
        new_attachments_names = []

        for attachment_name in attachments_names:
            new_unique_attachment_name = utils.generate_new_unique_file_name(
                file_name=attachment_name,
            )
            blob = self.bucket.blob(f"{self.blob_path}{new_unique_attachment_name}")
            if blob.exists() or new_unique_attachment_name in new_attachments_names:
                blob = utils.get_unique_blob(
                    bucket=self.bucket,
                    file_name=attachment_name,
                    list_of_names_to_compare=new_attachments_names,
                    path_name=self.blob_path
                )
            new_attachments_names.append(blob.name.replace(self.blob_path, "").strip())
        validated_data["attachments"] = new_attachments_names
        return super().create(validated_data)

    def update(self, instance, validated_data):
        fields_not_to_update = ["load", "creator"]
        for field in fields_not_to_update:
            if field in validated_data:
                del validated_data[field]
        attachments_names = validated_data.get("attachments", [])
        new_attachments_names = []
        if 'attachments' in validated_data:
            for attachment in instance.attachments:
                if attachment not in attachments_names:
                    blob = self.bucket.blob(f"{self.blob_path}{attachment}")
                    if blob.exists():
                        blob.delete()
            for attachment_name in attachments_names:
                if attachment_name not in instance.attachments:
                    new_unique_attachment_name = utils.generate_new_unique_file_name(
                        file_name=attachment_name,
                    )
                    blob = self.bucket.blob(f"{self.blob_path}{new_unique_attachment_name}")
                    if blob.exists() or new_unique_attachment_name in new_attachments_names:
                        blob = utils.get_unique_blob(
                            bucket=self.bucket,
                            list_of_names_to_compare=new_attachments_names,
                            file_name=attachment_name,
                            path_name=self.blob_path
                        )
                    new_attachments_names.append(blob.name.replace(self.blob_path, "").strip())
                else:
                    new_attachments_names.append(attachment_name)
            validated_data["attachments"] = new_attachments_names
        return super().update(instance, validated_data)

    def validate(self, data):
        message = data.get('message', '')
        if self.instance is None and message == '':
            raise serializers.ValidationError(
                {"IntegrityError": "You should provide a message with load note"}
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['creator'] = {
            "id": instance.creator.id,
            "username": instance.creator.user.username,
            "party_roles": get_app_user_load_party_roles(
                app_user=instance.creator,
                load=instance.load
            )
        }
        visible_to_parties = instance.visible_to.all()
        visible_to_representation = []
        for app_user in visible_to_parties:
            visible_to_representation.append({
                "id": app_user.id,
                "username": app_user.user.username,
                "party_roles": get_app_user_load_party_roles(
                    app_user=app_user,
                    load=instance.load
                )
            })
        representation["visible_to"] = visible_to_representation
        attachments_info = []
        for attachment_name in representation["attachments"]:
            attachments_info.append(
                {
                    "name": attachment_name,
                    "url": ""
                }
            )
        if request and request.method == 'POST':
            attachments_content_type = self.context.get('attachments_content_type')
            signed_urls = []
            content_types = []
            for i in range(len(representation["attachments"])):
                attachment_name = representation["attachments"][i]
                blob = self.bucket.blob(f"{self.blob_path}{attachment_name}")
                url = utils.generate_put_signed_url_for_file(
                    blob=blob,
                    content_type=attachments_content_type[i],
                    storage_client=self.storage_client,
                    headers={
                        "x-goog-meta-load_note_id": f'{instance.id}'
                    }
                )
                content_types.append(attachments_content_type[i])
                signed_urls.append(url)
            for i in range(len(attachments_info)):
                attachments_info[i]["url"] = signed_urls[i]
                attachments_info[i]["content_type"] = content_types[i]
        elif request and request.method == 'PATCH':
            attachments_content_type = self.context.get('attachments_content_type')
            signed_urls = []
            content_types = []
            for i in range(len(representation["attachments"])):
                attachment_name = representation["attachments"][i]
                blob = self.bucket.blob(f"{self.blob_path}{attachment_name}")
                url = ""
                content_type = ""
                if not blob.exists():
                    url = utils.generate_put_signed_url_for_file(
                        blob=blob,
                        content_type=attachments_content_type[i],
                        storage_client=self.storage_client,
                        headers={
                            "x-goog-meta-load_note_id": f'{instance.id}'
                        }
                    )
                    content_type = attachments_content_type[i]
                signed_urls.append(url)
                content_types.append(content_type)
            for i in range(len(attachments_info)):
                attachments_info[i]["url"] = signed_urls[i]
                attachments_info[i]["content_type"] = content_types[i]
            attachments_info = [item for item in attachments_info if item["url"]]
        else:
            for i in range(len(representation["attachments"])):
                attachment_name = representation["attachments"][i]
                blob = self.bucket.blob(f"{self.blob_path}{attachment_name}")
                url = ""
                content_type = ""
                if blob.exists():
                    url = utils.generate_get_signed_url_for_file(
                        blob=blob,
                        storage_client=self.storage_client,
                    )
                    blob.reload()
                    content_type = blob.content_type
                attachments_info[i]["url"] = url
                attachments_info[i]["content_type"] = content_type
        representation["attachments"] = attachments_info
        return representation


class LoadNoteAttachmentConfirmationSerializer(serializers.Serializer):
    load_note_id = serializers.IntegerField()
    attachment_name = serializers.CharField(max_length=255)


class LoadNoteAttachmentConfirmationClientSideSerializer(serializers.Serializer):
    load_note_id = serializers.IntegerField()
    attachments_names = serializers.ListField(child=serializers.CharField(max_length=255))


class LoadDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Load
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at")
        extra_kwargs = {
            "is_draft": {"default": True}
        }

    @staticmethod
    def validate_pickup_location(pickup_location: models.Facility, shipper: ShipmentParty):
        if pickup_location is not None and shipper is not None:
            if pickup_location.owner != shipper.app_user.user:
                raise serializers.ValidationError(
                    {"pickup_location": "The chosen facility doesn't belong to the shipper"})
        elif pickup_location is not None and shipper is None:
            raise serializers.ValidationError(
                {"pickup_location": "Can't have a pickup location without assigning a shipper"})

    @staticmethod
    def validate_destination_facility(destination: models.Facility, consignee: ShipmentParty):
        if destination is not None and consignee is not None:
            if destination.owner != consignee.app_user.user:
                raise serializers.ValidationError(
                    {"destination": "The chosen facility doesn't belong to the consignee"})
        elif destination is not None and consignee is None:
            raise serializers.ValidationError(
                {"destination": "Can't have a pickup location without assigning a consignee"})

    @staticmethod
    def validate_load_parties(load_parties, load_draft_creator: AppUser):
        for party, value in load_parties.items():
            if (
                    value is not None and
                    value.app_user != load_draft_creator and
                    not models.Contact.objects.filter(
                        origin=load_draft_creator.user,
                        contact=value.app_user
                    ).exists()
            ):
                raise serializers.ValidationError(
                    {
                        f"{value.app_user.user.username}": f"Is not in {load_draft_creator.user.username} contact list"
                    }
                )

    @staticmethod
    def validate_load_parties_tax_info(load_parties):
        for party, value in load_parties.items():
            if party in ["customer", "dispatcher"] and value is not None:
                try:
                    utils.get_user_tax_or_company(value.app_user, user_type=party)
                except exceptions.NotFound:
                    raise serializers.ValidationError(
                        {
                            party: "Has no tax information or a company."
                        }
                    )

    def validate(self, data):
        load_draft_creator = data["created_by"]
        pickup_location = data.get('pick_up_location', None)
        shipper = data.get('shipper', None)
        destination = data.get('destination', None)
        consignee = data.get('consignee', None)
        load_parties = {
            "customer": data.get('customer', None),
            "shipper": shipper,
            "consignee": consignee,
            "dispatcher": data.get('dispatcher', None)
        }
        self.validate_load_parties(load_parties, load_draft_creator)
        self.validate_load_parties_tax_info(load_parties)
        self.validate_pickup_location(pickup_location, shipper)
        self.validate_destination_facility(destination, consignee)
        return super().validate(data)

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if self.context['request'].method in ['PATCH']:
            extra_kwargs['name'] = {'required': False}
            extra_kwargs['created_by'] = {'required': False}
        return extra_kwargs

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            fields['created_by'].read_only = True
            fields['name'].read_only = True
        return fields

    def update(self, instance, validated_data):
        keys_to_get_deleted = ["created_by", "name"]
        for key in keys_to_get_deleted:
            if key in validated_data:
                del validated_data[key]
        return super().update(instance, validated_data)

    @staticmethod
    def get_load_parties_usernames(load: models.Load):
        load_parties = {
            "customer": load.customer,
            "shipper": load.shipper,
            "dispatcher": load.dispatcher,
            "carrier": load.carrier,
            "consignee": load.consignee,
        }
        result = {}
        for key, value in load_parties.items():
            result[key] = None
            if value is not None:
                result[key] = value.app_user.user.username
        return result

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["created_by"] = instance.created_by.user.username
        load_parties_usernames = self.get_load_parties_usernames(instance)
        for role, username in load_parties_usernames.items():
            rep[role] = username
        if instance.pick_up_location is not None:
            rep["pick_up_location"] = {
                "id": instance.pick_up_location.id,
                "building_name": instance.pick_up_location.building_name,
                "city": instance.pick_up_location.address.city,
                "state": instance.pick_up_location.address.state,
            }
        if instance.destination is not None:
            rep["destination"] = {
                "id": instance.destination.id,
                "building_name": instance.destination.building_name,
                "city": instance.destination.address.city,
                "state": instance.destination.address.state,
            }
        if instance.shipment is not None:
            rep["shipment"] = ShipmentSerializer(instance.shipment).data
        return rep


class ClaimNoteAttachmentConfirmationSerializer(serializers.Serializer):
    claim_note_id = serializers.IntegerField()
    supporting_doc = serializers.CharField(max_length=255)


class ClaimNoteAttachmentConfirmationClientSideSerializer(serializers.Serializer):
    claim_note_id = serializers.IntegerField()
    supporting_docs = serializers.ListField(child=serializers.CharField(max_length=255))


class ClaimAttachmentConfirmationSerializer(serializers.Serializer):
    claim_id = serializers.IntegerField()
    supporting_doc = serializers.CharField(max_length=255)


class ClaimAttachmentConfirmationClientSideSerializer(serializers.Serializer):
    claim_id = serializers.IntegerField()
    supporting_docs = serializers.ListField(child=serializers.CharField(max_length=255))
