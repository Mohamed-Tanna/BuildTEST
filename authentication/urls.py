from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
import authentication.views as views
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView


urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path(
        "account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_confirm_email_sent",
    ),
    path('password-reset/', PasswordResetView.as_view()),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "account-confirm-email/<key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("allauth/", include("allauth.urls")),
    path("app-user/", views.AppUserView.as_view()),
    path("base-user/<id>/", views.BaseUserView.as_view()),
    path("hc/", views.HealthCheckView.as_view()),
    path("shipment-party/", views.ShipmentPartyView.as_view()),
    path("carrier/", views.CarrierView.as_view()),
    path("broker/", views.BrokerView.as_view())
]
