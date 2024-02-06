from rest_framework.routers import DefaultRouter

from shipment.views import LoadNoteView, FacilityView, LoadView, LoadDraftView

load_router = DefaultRouter()
load_router.register(r'draft', LoadDraftView, basename='LoadDraft')
load_router.register(r'notes', LoadNoteView, basename='LoadNote')
load_router.register(r'', LoadView, basename='Load')


shipment_router = DefaultRouter()
shipment_router.register(r'facility', FacilityView, basename='Facility')
