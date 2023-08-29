# Module Imports
from .models import Ticket
from .serializers import TicketSerializer

# DRF imports
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

class ListTicketsView(GenericAPIView,ListModelMixin):
    """
    View for listing the Tickets
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RetrieveTicketsView(GenericAPIView,RetrieveModelMixin):
    """
    View for Retrieving the Tickets
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    lookup_field = "id"    
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class CreateTicketsView(GenericAPIView,CreateModelMixin):
    """
    View for Creating the Tickets
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
