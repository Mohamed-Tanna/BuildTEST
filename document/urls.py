from django.urls import path, include
import document.views as views

urlpatterns = [
    path("file/", views.FileUploadView.as_view()),
]