from django.urls import path
from support.views import CompanyView
from .views import ListCreateTicketsView, RetrieveTicketsView



urlpatterns = [
    path("create-company/", CompanyView.as_view()),
    path('list-create_tickets/', ListCreateTicketsView.as_view(), name='ticket-creation\listing'),
    path('retrive_tickets/', RetrieveTicketsView.as_view(), name='ticket-retrieval'),
    
]