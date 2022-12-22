from django.urls import path
from .views import *

urlpatterns = [
    path("facility/", FacilityView.as_view()),
    path("facility/<id>/", FacilityView.as_view()),
    path("load/", LoadView.as_view()),
    path("load/<id>/", LoadView.as_view()),
    path("contact/", ContactView.as_view()),
    path("load-facility/", LoadFacilityView.as_view()),
    path("load-contact/", ContactLoadView.as_view()),
    path("load-details/<id>/", RetrieveLoadView.as_view()),
]
