from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView



urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("admin/defender/", include("defender.urls")),
    path("freight-slayer-admin-sos-portal/", admin.site.urls),
    path("authentication/", include("authentication.urls")),
    path("shipment/", include("shipment.urls")),
    path("docs/", include("document.urls")),
    path("invites/", include("invitation.urls")),
]
