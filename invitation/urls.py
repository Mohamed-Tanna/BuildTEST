from django.urls import path
import invitation.views as views


urlpatterns = [
    path("send-invite/", views.CreateInvitationView.as_view()),
    path("handle-invite/", views.InvitationsHandlingView.as_view()),
    path("resend-invite/<id>/", views.ResendInvitationView.as_view()),
]
