from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # re_path(
    #     r"^docs/$",
    #     schema_view.with_ui("swagger", cache_timeout=0),
    #     name="schema-swagger-ui",
    # ),
    # re_path(
    #     r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    # ),
    path("admin/defender/", include("defender.urls")),
    path("freight-slayer-admin-sos-portal/", admin.site.urls),
    path("authentication/", include("authentication.urls")),
    path("shipment/", include("shipment.urls")),
    path("docs/", include("document.urls")),
]
