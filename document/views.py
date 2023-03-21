# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

# Django import
from django.db.models.query import QuerySet

# third party imports
from drf_yasg.utils import swagger_auto_schema

# module imports
import document.models as models
import shipment.models as ship_models
import document.serializers as serializers
import authentication.permissions as permissions



class FileUploadView(GenericAPIView, ListModelMixin):
    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    queryset = models.UploadedFile.objects.all()

    @swagger_auto_schema(
        operation_description="Upload a file to a load.",
        request_body=serializers.UploadFileSerializer,
        responses={
            200: serializers.UploadFileSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new file."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(request.data)
        
    
    @swagger_auto_schema(
        operation_description="Get all files related to a load.",
        responses={
            200: serializers.RetrieveFileSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
    )
    def get(self, request, *args, **kwargs):
        """Get all files related to a load."""
        load_id = request.query_params.get("load")
        if load_id:
            return self.list(request, *args, **kwargs)
        else:
            return Response([{"details": "load is required."}], status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        
        load_id = self.request.query_params.get("load")
        if load_id:
            try:
                load = ship_models.Load.objects.get(id=load_id)
                queryset = models.UploadedFile.objects.filter(load=load)
            except ship_models.Load.DoesNotExist:
                queryset = models.UploadedFile.objects.none()
        else:
            queryset = []
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.RetrieveFileSerializer
        elif self.request.method == "POST":
            return serializers.UploadFileSerializer
