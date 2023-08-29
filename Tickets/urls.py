from django.urls import path
from .views import TicketListView, TicketCreateView, TicketRetrieveView

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/create/', TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:id>/', TicketRetrieveView.as_view(), name='ticket-retrieve'),
]
