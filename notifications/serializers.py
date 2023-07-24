from rest_framework import serializers
import notifications.models as models
import authentication.serializers as auth_serializers


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = "__all__"
        extra_kwargs = {"seen": {"required": False}}
        read_only_fields = (
            "id",
            "created_at",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = auth_serializers.AppUserSerializer(instance.user).data
        return rep


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NotificationSetting
        fields = "__all__"
        extra_kwargs = {
            "is_allowed": {"required": False},
            "methods": {"required": False},
            "add_as_contact": {"required": False},
            "add_to_load": {"required": False},
            "got_offer": {"required": False},
            "offer_updated": {"required": False},
            "add_as_shipment_admin": {"required": False},
            "load_status_changed": {"required": False},
            "RC_approved": {"required": False},
            "updated_at": {"required": False},
        }
        read_only_fields = (
            "id",
            "updated_at",
            "user",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = auth_serializers.AppUserSerializer(instance.user).data
        return rep
