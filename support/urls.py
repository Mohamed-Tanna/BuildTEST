from django.urls import path
from support.views import CompanyView


urlpatterns = [
    path("create-company/", CompanyView.as_view()),
]