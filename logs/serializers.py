import logs.models as models
from rest_framework import serializers


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ["id", "app_user", "action", "model", "details", "timestamp"]
        read_only_fields = ["id", "app_user", "action", "model", "details", "timestamp"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["app_user"] = instance.app_user.user.username
        return data
