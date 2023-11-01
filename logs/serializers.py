import logs.models as models
from rest_framework import serializers

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ["id", "app_user", "action", "details", "timestamp"]
        read_only_fields = ["id", "app_user", "action", "details", "timestamp"]
