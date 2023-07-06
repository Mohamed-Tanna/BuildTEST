from rest_framework import serializers
import notifications.models as models
import authentication.serializers as auth_serializers

class Notification(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = "__all__"
        extra_kwargs = {"seen": {"required": False}}
        read_only_fields = ("id", "created_at",)
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = auth_serializers.AppUserSerializer(instance.user).data
        return rep 