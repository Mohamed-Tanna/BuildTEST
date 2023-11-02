from rest_framework import serializers
import manager.models as models
import authentication.models as auth_models
import shipment.utilities as ship_utils
import authentication.serializers as auth_serializers

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Insurance
        fields = '__all__'
        read_only_fields = ('id',)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["company"] = auth_serializers.CompanySerializer(instance.company).data


class ManagerContactListSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")
    tax_info = serializers.SerializerMethodField(method_name="get_tax_info")

    class Meta:
        model = auth_models.AppUser
        fields = [
            "id",
            "user",
            "phone_number",
            "user_type",
            "selected_role",
            "username",
            "email",
            "first_name",
            "last_name",
            "tax_info",
        ]
        read_only_fields = ("id",)

    def get_tax_info(self, obj: auth_models.AppUser):
        try:
            tax_info = ship_utils.get_user_tax_or_company(obj, user_type=obj.user_type)
            return tax_info
        except BaseException:
            tax_info = None
            return tax_info
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        tax_info = self.get_tax_info(instance)
        if isinstance(tax_info, auth_models.Company):
            rep["tax_info"] = auth_serializers.CompanySerializer(tax_info).data
        elif isinstance(tax_info, auth_models.UserTax):
            rep["tax_info"] = auth_serializers.UserTaxSerializer(tax_info).data
        rep["contact"] = auth_serializers.AppUserSerializer(instance).data
        del rep["id"]
        del rep["user"]
        del rep["phone_number"]
        del rep["user_type"]
        del rep["selected_role"]
        del rep["username"]
        del rep["email"]
        del rep["first_name"]
        del rep["last_name"]
        return rep
