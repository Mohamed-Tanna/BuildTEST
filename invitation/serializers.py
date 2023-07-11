from rest_framework import serializers
from authentication.serializers import AppUserSerializer
import invitation.models as models

class InvitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invitation
        fields = "__all__"

    def to_representation(self, instance: models.Invitation):
        rep = super().to_representation(instance)
        rep["inviter"] = AppUserSerializer(instance.inviter).data
        return rep