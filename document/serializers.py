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
                return Response(
                    [{"details": "File with this name already exists."}],
                    status=status.HTTP_409_CONFLICT,
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
                return Response(status=status.HTTP_201_CREATED)


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


class BrokerFinalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = ["__all__"]
        read_only_fields = (
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_full_name",
            "consignee_phone_number",
            "broker_full_name",
            "broker_phone_number",
            "broker_email",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "broker_company_name",
            "broker_company_address",
            "broker_company_fax_number",
            "carrier_company_name",
            "carrier_company_address",
            "carrier_company_fax_number",
            "customer_company_name",
            "customer_company_address",
            "customer_company_fax_number",
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
            "customer_offer",
            "carrier_offer",
            "did_customer_agree",
            "customer_uuid",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
            "load_type",
            "load_id",
        )


class CustomerFinalAgreement(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = [
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_full_name",
            "consignee_phone_number",
            "broker_full_name",
            "broker_phone_number",
            "broker_email",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "broker_company_name",
            "broker_company_address",
            "broker_company_fax_number",
            "customer_company_name",
            "customer_company_address",
            "customer_company_fax_number",
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
            "customer_offer",
            "did_customer_agree",
            "customer_uuid",
            "generated_at",
            "verified_at",
            "load_type",
            "load_id",
        ]
        read_only_fields = (
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_full_name",
            "consignee_phone_number",
            "broker_full_name",
            "broker_phone_number",
            "broker_email",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "broker_company_name",
            "broker_company_address",
            "broker_company_fax_number",
            "customer_company_name",
            "customer_company_address",
            "customer_company_fax_number",
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
            "customer_offer",
            "did_customer_agree",
            "customer_uuid",
            "generated_at",
            "verified_at",
            "load_type",
            "load_id",
        )


class CarrierFinalAgreement(serializers.ModelSerializer):
    class Meta:
        model = models.FinalAgreement
        fields = [
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_full_name",
            "consignee_phone_number",
            "broker_full_name",
            "broker_phone_number",
            "broker_email",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "broker_company_name",
            "broker_company_address",
            "broker_company_fax_number",
            "carrier_company_name",
            "carrier_company_address",
            "carrier_company_fax_number",
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
            "carrier_offer",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
            "load_type",
            "load_id",
        ]
        read_only_fields = (
            "shipper_full_name",
            "shipper_phone_number",
            "consignee_full_name",
            "consignee_phone_number",
            "broker_full_name",
            "broker_phone_number",
            "broker_email",
            "customer_full_name",
            "customer_phone_number",
            "customer_email",
            "carrier_full_name",
            "carrier_phone_number",
            "carrier_email",
            "broker_company_name",
            "broker_company_address",
            "broker_company_fax_number",
            "carrier_company_name",
            "carrier_company_address",
            "carrier_company_fax_number",
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
            "carrier_offer",
            "did_carrier_agree",
            "carrier_uuid",
            "generated_at",
            "verified_at",
            "load_type",
            "load_id",
        )
