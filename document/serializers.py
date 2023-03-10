from rest_framework import serializers
import document.models as models

class FileSerializer(serializers.Serializer):
    class Meta:
        model = models.UploadedFile
        fields = "__all__"
        read_only_fields = ("id",)


    