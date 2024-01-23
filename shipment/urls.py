from django.urls import path
import shipment.views as views

urlpatterns = [
    path("facility/", views.FacilityView.as_view()),
    path("facility/<id>/", views.FacilityView.as_view()),
    path("load/claim/claim-note/", views.ClaimNoteView.as_view()),
    path("load/claim/", views.ClaimView.as_view()),
    path("load/claim/<id>", views.ClaimView.as_view()),
    path("load/other-load-parties/", views.OtherLoadPartiesView.as_view()),
    path("load/notes/<id>/", views.LoadNoteView.as_view()),
    path("load/notes/", views.LoadNoteView.as_view()),
    path("load/", views.LoadView.as_view()),
    path("load/<id>/", views.LoadView.as_view()),
    path("list-load/", views.ListLoadView.as_view()),
    path("load-details/<id>/", views.RetrieveLoadView.as_view()),
    path("contact/", views.ContactView.as_view()),
    path("filter-facility/", views.FacilityFilterView.as_view()),
    path("filter-contact/", views.ContactFilterView.as_view()),
    path("filter-load/", views.LoadFilterView.as_view()),
    path("filter-shipment/", views.ShipmentFilterView.as_view()),
    path("admin/", views.ShipmentAdminView.as_view()),
    path("admin/<id>/", views.ShipmentAdminView.as_view()),
    path("offer/", views.OfferView.as_view()),
    path("offer/<id>/", views.OfferView.as_view()),
    path("reject-load/", views.DispatcherRejectView.as_view()),
    path("load-status/", views.UpdateLoadStatus.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("search-loads/", views.LoadSearchView.as_view()),
    path("search-contacts/", views.ContactSearchView.as_view()),
    # Fixed URL - always insert above
    path("<id>/", views.ShipmentView.as_view()),
    path("", views.ShipmentView.as_view()),
]
