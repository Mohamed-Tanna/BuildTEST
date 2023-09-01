from rest_framework import serializers
import support.models as models
from authentication.serializers import AddressSerializer

class TicketSerializer(serializers.ModelSerializer):
    company_address = AddressSerializer()

    class Meta:
        model = models.Ticket
        fields = ['firs_name','last_name', 'personal_phone','email', 'company_name', 'company_domain', 'company_size', 'company_address', 'EIN','company_phone_number']
