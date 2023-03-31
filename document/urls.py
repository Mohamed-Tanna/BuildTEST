from django.urls import path
import document.views as views

urlpatterns = [
    path("file/", views.FileUploadView.as_view()),
    path("billing/", views.BillingDocumnetsView.as_view()),
]