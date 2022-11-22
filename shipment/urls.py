from django.urls import path
from .views import *

urlpatterns = [
    path("facility/", FacilityView.as_view()),
    path("load/", LoadView.as_view()),
    path("load/<id>/", LoadView.as_view())
]
