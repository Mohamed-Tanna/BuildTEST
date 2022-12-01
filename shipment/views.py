# Module imports
from .models import *
from .serializers import *
from authentication.permissions import *

# Django imports
from django.db.models import Q
from django.http import QueryDict
from django.db.models.query import QuerySet

# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
)

# ThirdParty imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FacilityView(GenericAPIView, CreateModelMixin, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        IsShipmentParty,
    ]
    serializer_class = FacilitySerializer
    queryset = Facility.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "building_number",
                "building_name",
                "street",
                "city",
                "state",
                "zip_code",
                "country",
            ],
            properties={
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

        if self.request.query_params.__contains__("shipment-party"):
            queryset = Facility.objects.filter(
                owner=self.request.query_params.get("owner")
            )
        else:
            queryset = Facility.objects.filter(owner=self.request.user.id)
        if isinstance(queryset, QuerySet):
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
    GenericAPIView,
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]

    serializer_class = LoadSerializer
    queryset = Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):

        if self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

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

    # override
    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        app_user = AppUser.objects.get(user=self.request.user)
        if app_user.user_type == "shipment party":
            shipment_party = ShipmentParty.objects.get(app_user=app_user.id)
        elif app_user.user_type == "broker":
            broker = Broker.objects.get(app_user=app_user.id)
        elif app_user.user_type == "carrier":
            carrier = Carrier.objects.get(app_user=app_user.id)
        queryset = Load.objects.filter(
            Q(created_by=self.request.user.id)
            or Q(shipper=shipment_party)
            or Q(consignee=shipment_party)
            or Q(broker=broker)
            or Q(carreir=carrier)
        )
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class ContactView(GenericAPIView, CreateModelMixin, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        IsAppUser,
    ]

    queryset = Contact.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "contact",
            ],
            properties={
                "contact": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        """
        Add Contact
            Create a conatct for an **authenticated** user and add the contact to user's contact list

            **Example**
                >>> contact: Johndoe#4AEAT
        """
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["origin"] = request.user.id
        try:
            contact = User.objects.get(username=request.data["contact"])
        except User.DoesNotExist as e:
            return Response(
                {"details": ["User does not exist."]}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            contact = AppUser.objects.get(user=contact)
            request.data["contact"] = str(contact.id)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except AppUser.DoesNotExist as e:
            return Response(
                {
                    "details": [
                        "The user that you are trying to add has incomplete profile, please contact them before trying again."
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def perform_create(self, serializer):
        conatct = serializer.save()
        app_user = AppUser.objects.get(id=conatct.contact.id)
        origin_user = User.objects.get(id=app_user.user.id)
        contact_app_user = AppUser.objects.get(user=conatct.origin.id)
        Contact.objects.create(origin=origin_user, contact=contact_app_user)

    def get_queryset(self):

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        queryset = Contact.objects.filter(origin=self.request.user.id)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContactListSerializer
        elif self.request.method == "POST":
            return ContactCreateSerializer
