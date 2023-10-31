import manager.views as views
from django.urls import path
urlpatterns = [
    path("load/", views.ListEmployeesLoadsView.as_view()),
    path("load/<id>/", views.RetrieveEmployeeLoadView.as_view()),
    path("contacts/", views.ListEmployeesContactsView.as_view()),
    path("facilities/", views.ListEmployeesFacilitiesView.as_view()),
    path("shipment/<id>/", views.RetrieveEmployeeShipmentView.as_view()),
    path("shipment/", views.ListEmployeesShipmentsView.as_view()),
    path("file/", views.EmployeeFileUploadedView.as_view()),
    path("billing/", views.EmployeeBillingDocumentsView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
]
