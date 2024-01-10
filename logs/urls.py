from django.urls import path
import logs.views as views

urlpatterns = [
    path("list/", views.ListLogsView.as_view()),
    path("log/<id>/", views.ListLogsView.as_view()),
]
