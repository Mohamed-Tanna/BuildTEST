from django.urls import path
import notifications.views as views

urlpatterns = [
    path("settings/", views.NotificationSettingView.as_view()),
    path("settings/<id>/", views.NotificationSettingView.as_view()),
    # Fixed URL - always insert above
    path("", views.NotificationView.as_view()),
]