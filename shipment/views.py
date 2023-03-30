# Module imports
import shipment.models as models
import shipment.utilities as utils
import document.models as doc_models
import shipment.serializers as serializers
import authentication.models as auth_models
import authentication.permissions as permissions
from authentication.utilities import create_address

# Django imports
from django.db.models import Q
from django.http import QueryDict
from django.db import IntegrityError
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

# ThirdParty imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

ASSINING_CARRIER = "Assigning Carrier"
AWAITING_CUSTOMER = "Awaiting Customer"
AWAITING_CARRIER = "Awaiting Carrier"
SHIPMENT_PARTY = "shipment party"
ERR_FIRST_PART = "should either include a `queryset` attribute,"
ERR_SECOND_PART = "or override the `get_queryset()` method."


class FacilityView(
    GenericAPIView, CreateModelMixin, ListModelMixin, RetrieveModelMixin
):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentParty,
    ]
    lookup_field = "id"
    queryset = models.Facility.objects.all()
    serializer_class = serializers.FacilitySerializer

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

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return a list of facilities or a specific facility based on a given ID.",
                serializers.FacilitySerializer,
            ),
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def get(self, request, *args, **kwargs):
        """
        List all facilities the belong to the authenticated user.
        """

        if self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        queryset = models.Facility.objects.filter(owner=self.request.user.id)

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["owner"] = request.user.id
        address = create_address(
            building_number=request.data["building_number"],
            street=request.data["street"],
            city=request.data["city"],
            state=request.data["state"],
            country=request.data["country"],
            zip_code=request.data["zip_code"],
        )

        if address == False:
            return Response(
                [
                    {
                        "details": "Address creation failed. Please try again; if the issue persists please contact us ."
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        del (
            request.data["building_number"],
            request.data["street"],
            request.data["city"],
            request.data["state"],
            request.data["country"],
            request.data["zip_code"],
        )
        request.data["address"] = str(address.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class LoadView(GenericAPIView, CreateModelMixin, UpdateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.LoadCreateRetrieveSerializer
    queryset = models.Load.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "shipment",
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
                "shipment": openapi.Schema(type=openapi.TYPE_STRING),
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
                "created_by": openapi.Schema(type=openapi.TYPE_STRING),
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "shipper": openapi.Schema(type=openapi.TYPE_STRING),
                "consignee": openapi.Schema(type=openapi.TYPE_STRING),
                "broker": openapi.Schema(type=openapi.TYPE_STRING),
                "carrier": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_date": openapi.Schema(type=openapi.TYPE_STRING),
                "delivery_date": openapi.Schema(type=openapi.TYPE_STRING),
                "pick_up_location": openapi.Schema(type=openapi.TYPE_STRING),
                "destination": openapi.Schema(type=openapi.TYPE_STRING),
                "height": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "width": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "weight": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "depth": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "quantity": openapi.Schema(type=openapi.FORMAT_DECIMAL),
                "goods_info": openapi.Schema(type=openapi.TYPE_STRING),
                "load_type": openapi.Schema(type=openapi.TYPE_STRING),
                "status": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                "Return the updated Load.", serializers.LoadCreateRetrieveSerializer
            ),
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

        app_user = models.AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)
        request.data["name"] = utils.generate_load_name()
        parties_tax_info = utils.get_parties_tax(
            customer_username=request.data["customer"],
            broker_username=request.data["broker"],
        )
        if isinstance(parties_tax_info, Response):
            return parties_tax_info

        required_fields = ["shipper", "consignee", "customer"]
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"detail": [f"{field} is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            party = utils.get_shipment_party_by_username(username=request.data[field])
            request.data[field] = str(party.id)

        if "broker" not in request.data:
            return Response(
                {"detail": ["broker is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        broker = utils.get_broker_by_username(username=request.data["broker"])
        if not isinstance(broker, models.Broker):
            return broker
        request.data["broker"] = str(broker.id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except IntegrityError:
            request.data["name"] = utils.generate_load_name()
            self.perform_create(serializer)

        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")

            if "delivery_date_check" in str(e.__cause__):
                return Response(
                    {
                        "detail": [
                            "Invalid pick up or drop off date's, please double check the dates and try again"
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            elif "pick up location" in str(e.__cause__):
                return Response(
                    {
                        "detail": [
                            "pick up location and drop off location cannot be equal, please double check the locations and try again"
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"detail": [f"{e.args[0]}"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    # override
    def update(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        instance = self.get_object()

        if instance.status == "Created":
            return self._update_created_load(request, instance, kwargs)

        elif instance.status == ASSINING_CARRIER:
            return self._update_assigning_carrier_load(request, instance, kwargs)

        else:
            return Response(
                [
                    {"details": "You cannot update this load."},
                ],
                status=status.HTTP_403_FORBIDDEN,
            )

    def _update_created_load(self, request, instance, kwargs):
        party_types = ["customer", "shipper", "consignee"]
        new_request = self._handle_shipment_parties(request, party_types)
        if isinstance(new_request, Response):
            return new_request
        request = new_request

        if "broker" in request.data:
            broker = utils.get_broker_by_username(username=request.data["broker"])
            if isinstance(broker, Response):
                return broker
            else:
                request.data["broker"] = str(broker.id)

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # check that the user requesting to update the load is the one who created it
        user = models.AppUser.objects.get(user=self.request.user.id)

        if instance.created_by == user:
            self.perform_update(serializer)

        else:
            return Response(
                {
                    "detail": [
                        "The load you are trying to update does not exist or you are not the creator of this load."
                    ]
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def _update_assigning_carrier_load(self, request, instance, kwargs):

        if "carrier" not in request.data:
            return Response(
                [
                    {"details": "Carrier is required."},
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "action" not in request.data or request.data["action"] != "assign carrier":
            return Response(
                [
                    {
                        "details": "You cannot update the carrier unless you specify an action."
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        editor = utils.get_broker_by_username(username=request.user.username)

        if isinstance(editor, Response):
            return editor

        carrier = utils.get_carrier_by_username(username=request.data["carrier"])
        tax_info = utils.get_user_tax_or_company(carrier.app_user)

        if isinstance(tax_info, Response):
            return Response(
                {"details": "Carrier does not have a tax id or company name."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(carrier, Response):
            return carrier

        del request.data["action"]
        request.data["carrier"] = str(carrier.id)
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if instance.broker == editor:
            self.perform_update(serializer)

        else:
            return Response(
                {
                    "detail": [
                        "You cannot add a carrier to this load because you are not the assigend broker."
                    ]
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def _handle_shipment_parties(self, request, party_types):
        for party_type in party_types:
            if party_type in request.data:
                party = utils.get_shipment_party_by_username(
                    username=request.data[party_type]
                )
                if isinstance(party, Response):
                    return party

                if party_type == "customer":
                    app_user = utils.get_app_user_by_username(username=request.data[party_type])
                    party_tax = utils.get_user_tax_or_company(app_user=app_user)
                    if isinstance(party_tax, Response):
                        return party_tax
                    request.data[party_type] = str(party.id)

                request.data[party_type] = str(party.id)

        return request

class ListLoadView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    serializer_class = serializers.LoadListSerializer
    queryset = models.Load.objects.all()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Returns a load list.",
                serializers.LoadListSerializer,
            ),
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def get(self, request, *args, **kwargs):
        """
        List all loads related to a user to be represented in a table.

            taking the authenticated user and listing all of the loads that he is a part of either a shipper,
            a consignee, a broker or even the ones he created.
        """

        return self.list(request, *args, **kwargs)

    # override
    def get_queryset(self):
        queryset = self.queryset

        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        app_user = models.AppUser.objects.get(user=self.request.user.id)
        filter_query = Q(created_by=app_user.id)

        if app_user.user_type == SHIPMENT_PARTY:
            try:
                shipment_party = models.ShipmentParty.objects.get(app_user=app_user.id)
                filter_query |= (
                    Q(shipper=shipment_party.id)
                    | Q(consignee=shipment_party.id)
                    | Q(customer=shipment_party.id)
                )
            except models.ShipmentParty.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")

        elif app_user.user_type == "broker":
            try:
                broker = models.Broker.objects.get(app_user=app_user.id)
                filter_query |= Q(broker=broker.id)
            except models.Broker.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")

        elif app_user.user_type == "carrier":
            try:
                carrier = models.Carrier.objects.get(app_user=app_user.id)
                filter_query |= Q(carrier=carrier.id)
            except (models.Carrier.DoesNotExist) as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")

        queryset = (
            queryset.filter(filter_query).exclude(status="Canceled").order_by("-id")
        )

        return queryset


class RetrieveLoadView(
    GenericAPIView,
    RetrieveModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    serializer_class = serializers.LoadCreateRetrieveSerializer
    queryset = models.Load.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.",
                serializers.LoadCreateRetrieveSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def get(self, request, *args, **kwargs):

        return self.retrieve(request, *args, **kwargs)


class ContactView(GenericAPIView, CreateModelMixin, ListModelMixin, DestroyModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    queryset = models.Contact.objects.all()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.",
                serializers.ContactListSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
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
        responses={
            200: openapi.Response(
                "Return the created contact object.",
                serializers.ContactCreateSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "DOES NOT EXIST",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Add Contact
            Create a conatct for an **authenticated** user and add the contact to user's contact list

            **Example**
                >>> contact: Johndoe#4AEAT
        """
        return self.create(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["origin"] = request.user.id
        try:
            contact = models.User.objects.get(username=request.data["contact"])
        except models.User.DoesNotExist:
            return Response(
                {"details": ["User does not exist."]}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            if contact.id == request.data["origin"]:
                return Response(
                    {"details": ["Oops, you cannot add yourself!"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                origin = utils.get_app_user_by_username(request.user.username)
                contact = models.AppUser.objects.get(user=contact.id)
                if origin.user_type == "carrier":
                    if contact.user_type == SHIPMENT_PARTY:
                        return Response(
                            [
                                {
                                    "details": "You cannot add customers or shipment parties to your contact list."
                                },
                            ],
                            status=status.HTTP_403_FORBIDDEN,
                        )

                elif origin.user_type == SHIPMENT_PARTY:
                    if contact.user_type == "carrier":
                        return Response(
                            [
                                {
                                    "details": "You cannot add carriers to your contact list."
                                },
                            ],
                            status=status.HTTP_403_FORBIDDEN,
                        )

                request.data["contact"] = contact.id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )

        except models.AppUser.DoesNotExist:
            return Response(
                {
                    "details": [
                        "The user that you are trying to add has incomplete profile, please contact them before trying again."
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    # override
    def perform_create(self, serializer):
        conatct = serializer.save()
        app_user = models.AppUser.objects.get(id=conatct.contact.id)
        origin_user = models.User.objects.get(id=app_user.user.id)
        contact_app_user = models.AppUser.objects.get(user=conatct.origin.id)
        models.Contact.objects.create(origin=origin_user, contact=contact_app_user)

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        queryset = models.Contact.objects.filter(origin=self.request.user.id)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ContactListSerializer
        elif self.request.method == "POST":
            return serializers.ContactCreateSerializer


class ShipmentView(
    GenericAPIView,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.ShipmentSerializer
    queryset = models.Shipment.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Returns a list of shipments.", serializers.ShipmentSerializer
            ),
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        }
    )
    def get(self, request, *args, **kwargs):
        """
        List all shipments that is created by the authenticated user
        """
        if self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"name": openapi.Schema(type=openapi.TYPE_STRING)},
            required=[
                "name",
            ],
        ),
        responses={
            200: openapi.Response(
                "Return the created shipment.",
                serializers.ShipmentSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Create a shipment.

            **Example**
            >>> "name": "shipment name"
        """
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.TYPE_STRING,
                "status": openapi.TYPE_STRING,
                "created_by": openapi.TYPE_INTEGER,
            },
        ),
        responses={
            200: openapi.Response(
                "Return the updated shipment.",
                serializers.ShipmentSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def put(self, request, *args, **kwargs):
        """
        Update a shipment.
            update a shipment by changing the user who created this shipment status

            **Example**
            >>> "created_by": "username#00000"
        """
        return self.partial_update(request, *args, **kwargs)

    # override
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        app_user = models.AppUser.objects.get(user=request.user.id)
        admins = models.ShipmentAdmin.objects.filter(
            shipment=self.kwargs["id"]
        ).values_list("admin", flat=True)

        if str(instance.created_by) == app_user.user.username or app_user.id in admins:
            return Response(serializer.data)

        else:
            return Response(
                {
                    "detail": [
                        "You are not the creator nor and admin of this Load",
                    ]
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    # override
    def get_queryset(self):
        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        app_user = models.AppUser.objects.get(user=self.request.user.id)
        shipments = models.ShipmentAdmin.objects.filter(admin=app_user.id).values_list(
            "shipment", flat=True
        )
        queryset = models.Shipment.objects.filter(
            created_by=app_user.id
        ) | models.Shipment.objects.filter(id__in=shipments)

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset.order_by("-id")

    # override
    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = models.AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)
        request.data["status"] = "Created"
        request.data["name"] = utils.generate_shipment_name()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        while True:
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )
            except IntegrityError:
                request.data["name"] = utils.generate_shipment_name()
                continue
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(
                    {"detail": [f"{e.args[0]}"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    # override -- UNCOMPLETED
    def update(self, request, *args, **kwargs):
        """
        For future implementation
        """
        pass


class ShipmentFilterView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.ShipmentSerializer
    queryset = models.Shipment.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "keyword": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.",
                serializers.ShipmentSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        List your shipments base on a keyword.
            List your shipments based on a keyword that represents the shipment's name.

            **Example**
                >>> "keyword": "xyz"
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        try:
            app_user = models.AppUser.objects.get(user=self.request.user.id)
        except models.AppUser.DoesNotExist:
            queryset = []
            return queryset

        shipments = models.ShipmentAdmin.objects.filter(admin=app_user.id).values_list(
            "shipment", flat=True
        )

        keyword = ""
        if "keyword" in self.request.data:
            keyword = self.request.data["keyword"]

        queryset = models.Shipment.objects.filter(
            created_by=app_user.id, name__icontains=keyword
        ) | models.Shipment.objects.filter(id__in=shipments)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class FacilityFilterView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.FacilityFilterSerializer
    queryset = models.Facility.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "shipper": openapi.Schema(type=openapi.TYPE_STRING),
                "consignee": openapi.Schema(type=openapi.TYPE_STRING),
                "keyword": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                "Return the facility name, state and city.",
                serializers.FacilityFilterSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        List Facilities for the purpose of creating a Load.
            List the facilities while filtering them based on a shipper, consignee, or both. Both facilities are
            required for the creation of any load.

            **Example**
                >>> "keyword": "xyz"
                >>> "shipper": "username#00000"
        """
        return self.list(request, *args, **kwargs)

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        keyword = ""
        if "keyword" in self.request.data:
            keyword = self.request.data["keyword"]
        if "shipper" in self.request.data:
            username = self.request.data["shipper"]
            try:
                shipper = models.User.objects.get(username=username)
                queryset = models.Facility.objects.filter(
                    owner=shipper.id, building_name__icontains=keyword
                ).order_by("building_name")
            except models.User.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
                queryset = []
        elif "consignee" in self.request.data:
            username = self.request.data["consignee"]
            try:
                consignee = models.User.objects.get(username=username)
                queryset = models.Facility.objects.filter(
                    owner=consignee.id, building_name__icontains=keyword
                ).order_by("building_name")
            except models.User.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
                queryset = []
        else:
            queryset = []

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class ContactFilterView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.ContactListSerializer
    queryset = models.Contact.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "keyword": openapi.Schema(type=openapi.TYPE_STRING),
                "shipment": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.",
                serializers.ContactListSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        List a specific type of contacts for the purpose of searching.
            List the contacts while filtering them based on their user type and their usernames.

            **Example**
                >>> "type": "shipment party"
                >>> "keyword": "xyz"
        """
        return self.list(request, *args, **kwargs)

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        if "type" in self.request.data:
            user_type = self.request.data["type"]
            keyword = ""
            if "keyword" in self.request.data:
                keyword = self.request.data["keyword"]
            if "tax" in self.request.data:
                contacts = models.Contact.objects.filter(
                    origin=self.request.user.id,
                    contact__user_type=user_type,
                    contact__user__username__icontains=keyword,
                ).values_list("contact", flat=True)
                tax_query = (
                    Q(companyemployee__isnull=False) | Q(usertax__isnull=False)
                ) & (Q(id__in=contacts))
                tax_app_users = models.AppUser.objects.filter(tax_query).values_list(
                    "id", flat=True
                )
                queryset = models.Contact.objects.filter(
                    contact__in=tax_app_users,
                )
            else:
                queryset = models.Contact.objects.filter(
                    origin=self.request.user.id,
                    contact__user_type=user_type,
                    contact__user__username__icontains=keyword,
                )

        # if the request is intended to add a shipment party or a broker as shipment admins to a shipment
        elif "shipment" in self.request.data:
            keyword = ""
            if "keyword" in self.request.data:
                keyword = self.request.data["keyword"]

            queryset = models.Contact.objects.filter(
                origin=self.request.user.id,
                contact__user_type=SHIPMENT_PARTY,
                contact__user__username__icontains=keyword,
            ) | models.Contact.objects.filter(
                origin=self.request.user.id,
                contact__user_type="broker",
                contact__user__username__icontains=keyword,
            )
        else:
            queryset = []
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class LoadFilterView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.LoadListSerializer
    queryset = models.Load.objects.all()

    def post(self, request, *args, **kwargs):
        """List all loads depending on a certain value of a field

        **Args**:
            shipment: a shipment id to return all loads in a single shipment
            keyword: a keyword to return all loads that contains this keyword in its name

        **Returns**:
            list of loads: this endpoint will return a list of load objects
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.data

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        if "shipment" in data:
            shipment_id = data["shipment"]
            queryset = models.Load.objects.filter(shipment=shipment_id)
        elif "keyword" in data and "shipment" in data:
            keyword = data["keyword"]
            shipment_id = data["shipment"]
            queryset = models.Load.objects.filter(
                name__icontains=keyword, shipment=shipment_id
            )
        elif "keyword" in data:
            keyword = data["keyword"]
            app_user = models.AppUser.objects.get(user=self.request.user.id)
            queryset = models.Load.objects.filter(
                created_by=app_user.id, name__icontains=keyword
            )
        else:
            queryset = []
            return queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class OfferView(GenericAPIView, CreateModelMixin, UpdateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsAppUser,
    ]
    serializer_class = serializers.OfferSerializer
    queryset = models.Offer.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return the offer related to a load, you need to specify the load id in the kwargs",
                serializers.OfferSerializer,
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def get(self, request, *args, **kwargs):
        if self.kwargs:
            queryset = models.Offer.objects.filter(load=self.kwargs["id"])
            party = utils.get_app_user_by_username(username=request.user.username)
            if isinstance(party, models.AppUser):
                if party.user_type == "broker":
                    party = utils.get_broker_by_username(username=request.user.username)
                    if isinstance(party, models.Broker):
                        queryset = queryset.filter(party_1=party.id)
                    else:
                        return party
                else:
                    queryset = queryset.filter(party_2=party.id)

                queryset = queryset.exclude(status="Rejected").order_by("id")
                serializer = self.get_serializer(queryset, many=True)
                return Response(status=status.HTTP_200_OK, data=serializer.data)

            else:
                return party
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "party_1": openapi.Schema(type=openapi.TYPE_STRING),
                "party_2": openapi.Schema(type=openapi.TYPE_STRING),
                "initial": openapi.Schema(type=openapi.TYPE_INTEGER),
                "current": openapi.Schema(type=openapi.TYPE_INTEGER),
                "load": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["party_1", "party_2", "initial", "current", "load"],
        ),
        responses={
            200: openapi.Response(
                "Return the created offer.", serializers.OfferSerializer
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Create an offer on a load

            Create an offer on a load if you are the broker assigned to this load you can create an offer for both shipper and carrier
            using this endpoint.
        """
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "current": openapi.Schema(type=openapi.TYPE_INTEGER),
                "action": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "action",
            ],
        ),
        responses={
            200: openapi.Response(
                "Return the updated offer.", serializers.OfferSerializer
            ),
            400: "BAD REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def put(self, request, *args, **kwargs):

        return self.partial_update(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        broker = utils.get_broker_by_username(username=request.user.username)

        if isinstance(broker, Response):
            return Response(
                [
                    {
                        "details": "you cannot create an offer since your are not a broker"
                    },
                ],
                status=status.HTTP_403_FORBIDDEN,
            )

        request.data["party_1"] = broker.id
        load = models.Load.objects.get(id=request.data["load"])

        if load.broker is None:
            return Response(
                [
                    {
                        "details": "Please add a broker to this load before creating a bid on it"
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        if load.broker != broker:
            return Response(
                [
                    {
                        "details": "you cannot create an offer since you're not the broker assigned to this load"
                    },
                ],
                status=status.HTTP_403_FORBIDDEN,
            )

        if load.status == "Created":
            return self._create_offer_for_customer(request, load)

        elif load.status == ASSINING_CARRIER:
            return self._create_offer_for_carrier(request, load)

        else:
            return Response(
                [
                    {"details": "This load is no longer open for bidding"},
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

    # override
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        load = models.Load.objects.get(id=instance.load.id)

        if instance.status != "Pending":
            return Response(
                [
                    {
                        "details": "This offer is already closed, something must have gone wrong.",
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "action" not in request.data:
            return Response(
                [{"details": "action required"}], status=status.HTTP_400_BAD_REQUEST
            )

        if request.data["action"] == "accept":
            return self._process_accept_action(request, load, instance, partial)

        elif request.data["action"] == "reject":
            return self._process_reject_action(request, load, instance, partial)

        elif request.data["action"] == "counter":
            return self._proccess_counter_action(request, load, instance, partial)

        else:
            return Response(
                [{"details": "Unknown action"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _process_accept_action(self, request, load, instance, partial):
        if load.status == AWAITING_CUSTOMER:
            load.status = ASSINING_CARRIER
            load.save()
        elif load.status == AWAITING_CARRIER:
            load.status = "Ready For Pick Up"
            load.save()
            self._create_final_agreement(load=load)
        elif load.status == "Awaiting Broker":
            if instance.party_2.user_type == SHIPMENT_PARTY:
                load.status = ASSINING_CARRIER
                load.save()
            elif instance.party_2.user_type == "carrier":
                load.status = "Ready For Pick Up"
                load.save()
                self._create_final_agreement(load=load)
        else:
            return Response(
                [
                    {
                        "details": "This load is no longer open for bidding",
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        del request.data["action"]
        request.data["status"] = "Accepted"
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def _process_reject_action(self, request, load, instance, partial):
        user = utils.get_app_user_by_username(username=request.user.username)
        if user.user_type == "carrier":
            load.status = ASSINING_CARRIER
            load.carrier = None
            load.save()
        else:
            load.status = "Canceled"
            load.save()

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        del request.data["action"]
        request.data["status"] = "Rejected"
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def _proccess_counter_action(self, request, load, instance, partial):
        app_user = utils.get_app_user_by_username(request.user.username)
        if app_user.user_type == SHIPMENT_PARTY or app_user.user_type == "carrier":
            load.status = "Awaiting Broker"
            load.save()
        elif app_user.user_type == "broker":
            if instance.party_2.user_type == SHIPMENT_PARTY:
                load.status = AWAITING_CUSTOMER
                load.save()
            elif instance.party_2.user_type == "carrier":
                load.status = AWAITING_CARRIER
                load.save()

        del request.data["action"]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def _create_offer_for_customer(self, request, load):
        shipper = utils.get_shipment_party_by_username(request.data["party_2"])

        if isinstance(shipper, models.ShipmentParty):
            if load.customer == shipper or load.created_by == shipper:
                request.data["current"] = request.data["initial"]
                shipper = utils.get_app_user_by_username(request.data["party_2"])
                request.data["party_2"] = shipper.id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                load.status = AWAITING_CUSTOMER
                load.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )

            else:
                return Response(
                    [
                        {
                            "details": "This user is not the customer nor the creator of this load"
                        },
                    ],
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:
            return Response(
                [
                    {
                        "details": "The first bid has to have the 'customer' as the second party"
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _create_offer_for_carrier(self, request, load):
        carrier = utils.get_carrier_by_username(request.data["party_2"])

        if isinstance(carrier, models.Carrier):
            if load.carrier is not None and load.carrier == carrier:
                request.data["current"] = request.data["initial"]
                carrier = utils.get_app_user_by_username(request.data["party_2"])
                request.data["party_2"] = str(carrier.id)
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                load.status = AWAITING_CARRIER
                load.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )

            else:
                return Response(
                    [
                        {
                            "details": "This load does not have a carrier yet or this carrier is not the carrier assigned to this load"
                        },
                    ],
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                [
                    {
                        "details": "The second bid has to have the 'carrier' as the second party"
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _create_final_agreement(self, load):
        shipper = load.shipper
        consignee = load.consignee
        carrier = load.carrier
        broker = load.broker
        customer = load.customer
        pickup_facility = load.pick_up_location
        drop_off_facility = load.destination
        broker_billing = utils.get_user_tax_or_company(app_user=broker)
        if isinstance(broker_billing, Response):
            return broker_billing
        broker_billing = utils.extract_billing_info(broker_billing, broker)
        carrier_billing = utils.get_user_tax_or_company(app_user=carrier)
        if isinstance(carrier_billing, Response):
            return carrier_billing
        carrier_billing = utils.extract_billing_info(carrier_billing, carrier)
        customer_billing = utils.get_user_tax_or_company(app_user=customer)
        if isinstance(customer_billing, Response):
            return customer_billing

        customer_offer = get_object_or_404(
            models.Offer, load=load, party_2=customer.app_user
        )
        carrier_offer = get_object_or_404(
            models.Offer, load=load, party_2=carrier.app_user
        )
        doc_models.FinalAgreement.objects.create(
            load_id=load.id,
            shipper_username=shipper.app_user.user.username,
            shipper_full_name=shipper.app_user.user.first_name
            + " "
            + shipper.app_user.user.last_name,
            shipper_phone_number=shipper.app_user.phone_number,
            consignee_username=consignee.app_user.user.username,
            consignee_full_name=consignee.app_user.user.first_name
            + " "
            + consignee.app_user.user.last_name,
            consignee_phone_number=consignee.app_user.phone_number,
            broker_username=broker.app_user.user.username,
            broker_full_name=broker.app_user.user.first_name
            + " "
            + broker.app_user.user.last_name,
            broker_phone_number=broker.app_user.phone_number,
            broker_email=broker.app_user.user.email,
            customer_username=customer.app_user.user.username,
            customer_full_name=customer.app_user.user.first_name
            + " "
            + customer.app_user.user.last_name,
            customer_phone_number=customer.app_user.phone_number,
            customer_email=customer.app_user.user.email,
            carrier_username=carrier.app_user.user.username,
            carrier_full_name=carrier.app_user.user.first_name
            + " "
            + carrier.app_user.user.last_name,
            carrier_phone_number=carrier.app_user.phone_number,
            carrier_email=carrier.app_user.user.email,
            broker_billing_name=broker_billing["name"],
            broker_billing_address=broker_billing["address"],
            broker_billing_phone_number=broker_billing["phone_number"],
            carrier_billing_name=carrier_billing["name"],
            carrier_billing_address=carrier_billing["address"],
            carrier_billing_phone_number=carrier_billing["phone_number"],
            customer_billing_name=customer_billing["name"],
            customer_billing_address=customer_billing["address"],
            customer_billing_phone_number=customer_billing["phone_number"],
            shipper_facility_name=pickup_facility.building_name,
            shipper_facility_address=pickup_facility.address.building_number
            + ", "
            + pickup_facility.address.street
            + ", "
            + pickup_facility.address.city
            + ", "
            + pickup_facility.address.state
            + ", "
            + pickup_facility.address.zip_code,
            consignee_facility_name=drop_off_facility.building_name,
            consignee_facility_address=drop_off_facility.address.building_number
            + ", "
            + drop_off_facility.address.street
            + ", "
            + drop_off_facility.address.city
            + ", "
            + drop_off_facility.address.state
            + ", "
            + drop_off_facility.address.zip_code,
            pickup_date=load.pick_up_date,
            dropoff_date=load.delivery_date,
            length=load.length,
            width=load.width,
            height=load.height,
            weight=load.weight,
            quantity=load.quantity,
            commodity=load.commodity,
            goods_info=load.goods_info,
            customer_offer=customer_offer.current,
            carrier_offer=carrier_offer.current,
            load_type=load.load_type,
        )


class ShipmentAdminView(
    GenericAPIView,
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        permissions.IsShipmentPartyOrBroker,
    ]
    serializer_class = serializers.ShipmentAdminSerializer
    queryset = models.ShipmentAdmin.objects.all()

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "ShipmentAdminSerializer",
            status.HTTP_404_NOT_FOUND: "Not Found",
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get all shipment admins of a specific admin

            Provide a shipment id in the form of a query parameter and get a list of app users which are these shipment admins
        """
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=serializers.ShipmentAdminSerializer,
        responses={
            status.HTTP_201_CREATED: "ShipmentAdminSerializer",
            status.HTTP_400_BAD_REQUEST: "Validation Error",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Create a shipment admin and attach a shipment to it

            provide a username in the key **admin** and shipment id in the key **shipment**
        """
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=serializers.ShipmentAdminSerializer,
        responses={
            status.HTTP_201_CREATED: "ShipmentAdminSerializer",
            status.HTTP_400_BAD_REQUEST: "Validation Error",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
    )
    def put(self, request, *args, **kwargs):
        """
        Update a shipment admin
            **(CANCELED FEATURE)**
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete a shipment admin
        """

        return self.destroy(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        try:
            app_user = models.AppUser.objects.get(user=request.user.id)
        except models.AppUser.DoesNotExist:
            return Response(
                {"detail": ["user does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            shipment_id = request.data["shipment"]
            shipment = models.Shipment.objects.get(id=shipment_id)
        except models.Shipment.DoesNotExist:
            return Response(
                {"detail": ["shipment does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "admin" in request.data:
            admin = utils.get_app_user_by_username(request.data["admin"])
            request.data["admin"] = admin.id
        else:
            return Response(
                {"detail": ["admin is not specfied."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if shipment.created_by.id == app_user.id:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(
                {"detail": ["This user is not the owner of this shipment."]},
                status=status.HTTP_403_FORBIDDEN,
            )

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        if self.request.GET.get("id"):
            shipment_id = self.request.GET.get("id")
            queryset = models.ShipmentAdmin.objects.filter(shipment=shipment_id)
        else:
            queryset = []

        return queryset

    # override
    def update(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        if "admin" in request.data:
            admin = utils.get_app_user_by_username(request.data["admin"])
            request.data["admin"] = admin.id

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class BrokerRejectView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "load": openapi.Schema(type=openapi.TYPE_INTEGER, description="load id")
            },
        ),
        responses={
            status.HTTP_200_OK: "load canceled.",
            status.HTTP_400_BAD_REQUEST: "Validation Error",
            status.HTTP_403_FORBIDDEN: "Forbidden",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Broker reject a load
        """
        load_id = request.data["load"]
        load = get_object_or_404(models.Load, id=load_id)
        broker = load.broker.app_user.user
        if broker != request.user:
            return Response(
                {"detail": "This user is not the broker of this load."},
                status=status.HTTP_403_FORBIDDEN,
            )
        load.status = "Canceled"
        load.save()
        return Response({"detail": "load canceled."}, status=status.HTTP_200_OK)
