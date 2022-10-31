from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
from .views import *
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
    path("app-user/", AppUserView.as_view()),
    path("base-user/<id>/", BaseUserView.as_view()),
    path("hc/", HealthCheckView.as_view()),
    path("shipment-party/", ShipmentPartyView.as_view()),
    path("facility/", FacilityView.as_view()),
    path("carrier/", CarrierView.as_view())
]
