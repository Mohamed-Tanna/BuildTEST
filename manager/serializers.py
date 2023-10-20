from rest_framework import serializers
import manager.models as models
import authentication.serializers as auth_serializers

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Insurance
        fields = '__all__'
        read_only_fields = ('id',)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["company"] = auth_serializers.CompanySerializer(instance.company).data
