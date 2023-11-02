import manager.views as views
from django.urls import path
urlpatterns = [

    path("filter-load/", views.FilterEmployeeLoadsView.as_view()),
    path("search-loads/", views.ListEmployeesLoadsView.as_view()),
    path("load-details/<id>/", views.RetrieveEmployeeLoadView.as_view()),

    path("contact/", views.ListEmployeesContactsView.as_view()),
    path("search-contacts/", views.ListEmployeesContactsView.as_view()),

    path("facility/", views.ListEmployeesFacilitiesView.as_view()),
    path("search-facilities/", views.ListEmployeesFacilitiesView.as_view()),

    path("shipment/<id>/", views.ListEmployeesShipmentsView.as_view()),
    path("search-shipments/", views.ListEmployeesShipmentsView.as_view()),

    path("admin/", views.ListEmployeesShipmentAdminsView.as_view()),

    path("offer/<id>/", views.RetrieveEmployeeOfferView.as_view()),

    path("file/", views.EmployeeFileUploadedView.as_view()),

    path("billing/", views.EmployeeBillingDocumentsView.as_view()),

    path("dashboard/", views.DashboardView.as_view()),
]
