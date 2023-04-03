from django.urls import path
import document.views as views

urlpatterns = [
    path("file/", views.FileUploadView.as_view()),
    path("billing/", views.BillingDocumentsView.as_view()),
    path("validate-rc/", views.ValidateFinalAgreementView.as_view()),
]