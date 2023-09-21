from rest_framework import serializers
import document.models as models
import shipment.models as ship_models
import authentication.models as auth_models
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import document.utilities as utils


class UploadFileSerializer(serializers.Serializer):
    uploaded_file = serializers.FileField()

    class Meta:
        model = models.UploadedFile
        fields = [
            "id",
            "name",
            "uploaded_file",
            "load",
            "uploaded_by",
            "uploaded_at",
            "size",
        ]
        read_only_fields = (
            "id",
            "uploaded_at",
        )

    def create(self, validated_data):
        uploaded_file = validated_data["uploaded_file"]
        if uploaded_file.name == validated_data["name"]:
            load = get_object_or_404(ship_models.Load, id=validated_data["load"])
            # BOL_L-123456.pdf
            name = validated_data["name"].split(".")[0] + "_" + load.name + ".pdf"
            conflict = models.UploadedFile.objects.filter(name=name).exists()
            if conflict:
                raise serializers.ValidationError(
                    {"details": "File with this name already exists."}
                )
            else:
                uploaded_file.name = name
                utils.upload_to_gcs(uploaded_file)
                uploaded_by = get_object_or_404(
                    auth_models.AppUser, id=validated_data["uploaded_by"]
                )
                obj = models.UploadedFile.objects.create(
                    name=name,
                    load=load,
                    uploaded_by=uploaded_by,
                    size=validated_data["size"],
                )
                obj.save()
                return obj


class RetrieveFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.UploadedFile
        fields = [
            "id",
            "name",
            "url",
            "uploaded_by",
            "uploaded_at",
            "size",
        ]

    def get_url(self, obj):
        url = utils.generate_signed_url(object_name=obj.name)
        return url if url else "unavailable"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["uploaded_by"] = instance.uploaded_by.user.username
        return rep


class DispatcherFinalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = "__all__"
        read_only_fields = (
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "customer_username",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "customer_billing_name",
            "customer_billing_address",
            "customer_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "customer_offer",
            "carrier_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        )


class CustomerFinalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = [
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "customer_username",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "customer_billing_name",
            "customer_billing_address",
            "customer_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "customer_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        ]
        read_only_fields = (
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "customer_username",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "customer_billing_name",
            "customer_billing_address",
            "customer_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "customer_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        )


class CarrierFinalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = [
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "carrier_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        ]
        read_only_fields = (
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "customer_username",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "customer_billing_name",
            "customer_billing_address",
            "customer_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "customer_offer",
            "carrier_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        )


class BOLSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = [
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "carrier_billing_address",
            "carrier_billing_phone_number",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "carrier_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        ]
        read_only_fields = (
            "shipper_username",
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_username",
            "consignee_full_name",
            "consignee_phone_number",
            "dispatcher_username",
            "dispatcher_full_name",
            "dispatcher_phone_number",
            "dispatcher_email",
            "carrier_username",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "dispatcher_billing_name",
            "dispatcher_billing_address",
            "dispatcher_billing_phone_number",
            "carrier_billing_name",
            "shipper_facility_name",
            "shipper_facility_address",
            "consignee_facility_name",
            "consignee_facility_address",
            "pickup_date",
            "dropoff_date",
            "length",
            "width",
            "height",
            "weight",
            "quantity",
            "commodity",
            "goods_info",
            "load_type",
            "load_id",
            "equipment",
            "load_name",
            "shipment_name",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
        )
