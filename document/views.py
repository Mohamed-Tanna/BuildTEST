# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

# third party imports
from drf_yasg.utils import swagger_auto_schema

# module imports
import document.models as models
import document.utilities as utils
import document.serializers as serializers
import authentication.permissions as permissions


class FileUploadView(GenericAPIView, CreateModelMixin):
    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    serializer_class = serializers.FileSerializer
    queryset = models.UploadedFile.objects.all()

    @swagger_auto_schema(
        operation_description="Upload a file to a load.",
        request_body=serializers.FileSerializer,
        responses={
            200: serializers.FileSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new file."""
        return self.create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Get all files related to a load.",
        responses={
            200: serializers.FileSerializer,
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
        if load_id is None:
            return Response(
                [
                    {"detail": "load is required."},
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_names = models.UploadedFile.objects.filter(load=load_id).values_list(
            "name", flat=True
        )

        if len(file_names) == 0:
            return Response(
                {"detail": ["this load does not have any files attached."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        urls = []
        for file_name in file_names:
            url = utils.generate_signed_url(object_name=file_name)
            if url is not None:
                urls.append(url)

        res = {}
        for i in range(len(file_names)):
            res[file_names[i]] = urls[i]

        return Response(data=res, status=status.HTTP_200_OK)
