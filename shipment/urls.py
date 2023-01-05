from django.urls import path
from .views import *

urlpatterns = [
    path("facility/", FacilityView.as_view()),
    path("facility/<id>/", FacilityView.as_view()),
    path("load/", LoadView.as_view()),
    path("load/<id>/", LoadView.as_view()),
    path("contact/", ContactView.as_view()),
    path("load-facility/", FacilityFilterView.as_view()),
    path("load-contact/", ContactFilterView.as_view()),
    path("load-shipment/", ShipmentFilterView.as_view()),
    path("load-details/<id>/", RetrieveLoadView.as_view()),
    path("", ShipmentView.as_view()),
    path("<id>/", ShipmentView.as_view()),
    path("admin/", ShipmentAdminView.as_view()),
    path("admin/<id>/", ShipmentAdminView.as_view()),
]
