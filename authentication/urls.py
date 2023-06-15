from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
import authentication.views as views
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from dj_rest_auth.registration.views import ResendEmailVerificationView


urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
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
    path("dispatcher/", views.DispatcherView.as_view()),
    path("company/", views.CompanyView.as_view()),
    path("user-tax/", views.UserTaxView.as_view()),
    path("company-employee/", views.CompanyEmployeeView.as_view()),
    path("check-company/", views.CheckCompanyView.as_view()),
    path("tax-info/", views.TaxInfoView.as_view()),
    path("add-role/", views.AddRoleView.as_view()),
    path("select-role/", views.SelectRoleView.as_view()),
    path("send-invite/", views.CreateInvitationView.as_view()),
    path("handle-invite/", views.InvitationsHandlingView.as_view()),
]
