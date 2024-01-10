from django.urls import path

import support.views as views

urlpatterns = [
    path("create-ticket/", views.CreateTicketView.as_view()),
    path("list-ticket/", views.ListTicketsView.as_view()),
    path("retrieve-ticket/<id>/", views.RetrieveTicketView.as_view()),
    path("handle-ticket/<id>/", views.HandleTicketView.as_view()),
    path("list-claims/", views.ListClaimView.as_view()),
]
