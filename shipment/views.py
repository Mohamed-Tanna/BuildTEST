from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from django.db.models.query import QuerySet
from django.http import QueryDict
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rolepermissions.mixins import HasRoleMixin
from rest_framework import status
from .models import *
from authentication.roles import *
from shipment.serializers import FacilitySerializer, LoadSerializer


class FacilityView(GenericAPIView, CreateModelMixin, ListModelMixin, HasRoleMixin):

    permission_classes = [
        IsAuthenticated,
    ]
    allowed_roles = [
        ShipmentPartyRole,
    ]

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

    def get_queryset(self):

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = Facility.objects.filter(owner=self.request.query_params.get("owner"))
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = AppUser.objects.get(user=request.user)
        request.data["owner"] = app_user.id

        if app_user.user_type == "shipment party":
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


class LoadView(
    GenericAPIView, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, HasRoleMixin
):

    permission_classes = [
        IsAuthenticated,
    ]
    allowed_roles = [
        BrokerRole,
        ShipmentPartyRole,
    ]

    serializer_class = LoadSerializer
    queryset = Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):

        return self.retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)

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
                "shipper",
                "consignee",
                "pick_up_date",
                "delivery_date",
                "pick_up_location",
                "destination",
                "height",
                "width",
                "depth",
            ],
            properties={
                "shipper": openapi.Schema(type=openapi.TYPE_STRING),
                "consignee": openapi.Schema(type=openapi.TYPE_STRING),
                "broker": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_date": openapi.Schema(type=openapi.TYPE_STRING),
                "delivery_date": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_location": openapi.Schema(type=openapi.TYPE_STRING),
                "destination": openapi.Schema(type=openapi.TYPE_STRING),
                "height": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "width": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "depth": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "quantity": openapi.Schema(type=openapi.FORMAT_DECIMAL),
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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "shipper": openapi.Schema(type=openapi.TYPE_STRING),
                "consignee": openapi.Schema(type=openapi.TYPE_STRING),
                "broker": openapi.Schema(type=openapi.TYPE_STRING),
                "carrier": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_date": openapi.Schema(type=openapi.TYPE_STRING),
                "delivery_date": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_location": openapi.Schema(type=openapi.TYPE_STRING),
                "destination": openapi.Schema(type=openapi.TYPE_STRING),
                "status": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: "OK",
            204: "NO CONTENT",
            304: "NOT MODIFIED",
            422: "UNPROCESSABLE ENTITY",
            400: "BAD REQUEST",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def put(self, request, *args, **kwargs):

        """
        Update load's shipper, consignee, broker, carrier, pick up location, destination, pick up date, delivery date

            Update the base user **shipper**, **consignee**, **broker**, **carrier**, **pick up location**, **destination**
            **pick up date** and **delivery date** either separately or all coupled together

            **Example**

                >>> carrier: carrier_id
                >>> broker: broker_id
        """
        return self.partial_update(request, *args, **kwargs)
