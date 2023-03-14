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
