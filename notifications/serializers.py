from rest_framework import serializers
import notifications.models as models
import authentication.serializers as auth_serializers


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = "__all__"
        extra_kwargs = {"seen": {"required": False}, "manager_seen": {"required": False}}
        read_only_fields = (
            "id",
            "created_at",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = auth_serializers.AppUserSerializer(instance.user).data
        rep["sender"] = auth_serializers.AppUserSerializer(instance.sender).data
        return rep


class ManagerNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "user",
            "sender",
            "message",
            "url",
            "seen",
            "created_at",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = auth_serializers.AppUserSerializer(instance.user).data
        rep["sender"] = auth_serializers.AppUserSerializer(instance.sender).data

        # handle message for manager
        new_message = rep["message"]
        if rep["message"].contains("has added you"):
            new_message = rep["message"].replace("has added you", f"has added your employee ({instance.user.user.first_name.capitalize()} {instance.user.user.last_name.capitalize()})")
        elif rep["message"].contains("has sent you"):
            new_message = rep["message"].replace("has sent you", f"has sent your employee ({instance.user.user.first_name.capitalize()} {instance.user.user.last_name.capitalize()})")
        elif rep["message"].contains("has countered your"):
            new_message = rep["message"].replace("has countered your", f"has countered your employee's ({instance.user.user.first_name.capitalize()} {instance.user.user.last_name.capitalize()})")
        elif rep["message"].contains("assigned you"):
            new_message = rep["message"].replace("assigned you", f"assigned your employee ({instance.user.user.first_name.capitalize()} {instance.user.user.last_name.capitalize()})")
        rep["message"] = new_message

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
