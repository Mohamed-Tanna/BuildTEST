from django.urls import path
from support.views import CompanyView
import support.views as views


urlpatterns = [
    path("create-company/", CompanyView.as_view()),
    path("create-ticket/", views.CreateTicketView.as_view()),
    path("list-ticket/", views.ListTicketsView.as_view()),
    path("retrieve-ticket/<id>/", views.RetrieveTicketView.as_view()),
    path("handle-ticket/<id>/", views.HandleTicketView.as_view()),
]
