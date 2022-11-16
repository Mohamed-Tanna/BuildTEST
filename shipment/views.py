from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from .models import *
from shipment.serializers import FacilitySerializer, LoadSerializer


class FacilityView(GenericAPIView, CreateModelMixin, ListModelMixin):
    
    permission_classes = [IsAuthenticated, ]

    serializer_class = FacilitySerializer
    queryset = Facility.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "owner",
                "building_number",
                "building_name",
                "street",
                "city",
                "state",
                "zip_code",
                "country",
            ],
            properties={
                "owner": openapi.Schema(type=openapi.TYPE_STRING),
                "building_number": openapi.Schema(type=openapi.TYPE_STRING),
                "building_name": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "city": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "zip_code": openapi.Schema(type=openapi.TYPE_STRING),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "extra_info": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "CREATED",
            400: "BAD REQUEST",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):

        """
        Create a Facility

            Create a **Facility** with an existing **Shipment Party** as its owner

            **Example**
                >>> facility: {facility: facility_object}
        """

        return self.create(request, *args, **kwargs)
    
    
    def get(self, request, *args, **kwargs):
        
        return self.list(request, *args, **kwargs)


class LoadView(GenericAPIView, CreateModelMixin):

    permission_classes = [IsAuthenticated, ]
    
    serializer_class = LoadSerializer
    queryset = Load.objects.all()

    def create(self, request, *args, **kwargs):

        app_user = request.data.get("creator")
        app_user = AppUser.objects.get(id=app_user)
        if app_user.user_type == "broker" or app_user.user_type == "shipment party":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(
                {
                    "user role": [
                        "User does not have the required role to preform this action"
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "owner",
                "pick_up_date",
                "delivery_date",
                "pick_up_location",
                "destination",
                "status",
            ],
            properties={
                "owner": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_date": openapi.Schema(type=openapi.TYPE_STRING),
                "delivery_date": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_location": openapi.Schema(type=openapi.TYPE_STRING),
                "destination": openapi.Schema(type=openapi.TYPE_STRING),
                "status": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "CREATED",
            400: "BAD REQUEST",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):

        """
        Create a Load

            Create a **Load** as its owner if your role is **Shipment Party** or **Broker**

            **Example**
                >>> load: {load: load_object}
        """

        return self.create(request, *args, **kwargs)
