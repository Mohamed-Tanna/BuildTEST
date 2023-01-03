# Module imports
from .models import *
from .utilities import *
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
    DestroyModelMixin,
)

# ThirdParty imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class FacilityView(
    GenericAPIView, CreateModelMixin, ListModelMixin, RetrieveModelMixin
):

    permission_classes = [
        IsAuthenticated,
        IsShipmentParty,
    ]
    lookup_field = "id"
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer

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
                "Return the contact list of a specific type.",
                FacilitySerializer,
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
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        queryset = Facility.objects.filter(owner=self.request.user.id)

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["owner"] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class LoadView(
    GenericAPIView,
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]
    queryset = Load.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Returns a load list.",
                LoadListSerializer,
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
                "Return the updated Load.", LoadCreateRetrieveSerializer
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

        app_user = AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)

        if "shipper" in request.data:
            username = request.data["shipper"]
            shipper = get_shipment_party_by_username(username=username)
            request.data["shipper"] = str(shipper.id)

        else:
            return Response(
                {"detail": ["shipper is requried."]}, status=status.HTTP_400_BAD_REQUEST
            )

        if "consignee" in request.data:
            username = request.data["consignee"]
            consignee = get_shipment_party_by_username(username=username)
            request.data["consignee"] = str(consignee.id)

        else:
            return Response(
                {"detail": ["consignee is requried."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "broker" in request.data:
            username = request.data["broker"]
            broker = get_broker_by_username(username=username)
            request.data["broker"] = str(broker.id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # check database constraints
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")

            if "delivery_date_check" in str(e.__cause__) or "pick_up_date" in str(
                e.__cause__
            ):
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

            else:
                return Response(
                    {"detail": [f"{e.args[0]}"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    # override
    def get_queryset(self):

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        app_user = AppUser.objects.get(user=self.request.user.id)
        filter_query = Q()
        filter_query.add(Q(created_by=app_user.id), Q.OR)
        if app_user.user_type == "shipment party":
            try:
                shipment_party = ShipmentParty.objects.get(app_user=app_user.id)
                filter_query.add(Q(shipper=shipment_party.id), Q.OR)
                filter_query.add(Q(consignee=shipment_party.id), Q.OR)
            except ShipmentParty.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
        elif app_user.user_type == "broker":
            try:
                broker = Broker.objects.get(app_user=app_user.id)
                filter_query.add(Q(broker=broker.id), Q.OR)
            except Broker.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
        elif app_user.user_type == "carrier":
            try:
                carrier = Carrier.objects.get(app_user=app_user.id)
                filter_query.add(Q(carrier=carrier.id), Q.OR)
            except Carrier.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")

        queryset = Load.objects.filter(filter_query).order_by("-id")
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    # override
    def update(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        if "shipper" in request.data:
            username = request.data["shipper"]
            shipper = get_shipment_party_by_username(username=username)
            if isinstance(shipper, Response):
                return shipper
            else:
                request.data["shipper"] = str(shipper.id)

        if "consignee" in request.data:
            username = request.data["consignee"]
            consignee = get_shipment_party_by_username(username=username)
            if isinstance(consignee, Response):
                return consignee
            else:
                request.data["consignee"] = str(consignee.id)

        if "broker" in request.data:
            username = request.data["broker"]
            broker = get_broker_by_username(username=username)
            if isinstance(broker, Response):
                return broker
            else:
                request.data["broker"] = str(broker.id)

        if "carrier" in request.data:
            username = request.data["carrier"]
            carrier = get_carrier_by_username(username=username)
            if isinstance(carrier, Response):
                return carrier
            else:
                request.data["carrier"] = str(carrier.id)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # check that the user requesting to update the load is the one who created it
        user = AppUser.objects.get(user=self.request.user.id)

        if Load.objects.filter(id=instance.id, created_by=user.id).exists():
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

    # override
    def get_serializer_class(self):
        if self.request.method == "GET":
            return LoadListSerializer
        elif self.request.method == "POST":
            return LoadCreateRetrieveSerializer
        else:
            return LoadCreateRetrieveSerializer


class RetrieveLoadView(
    GenericAPIView,
    RetrieveModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]
    serializer_class = LoadCreateRetrieveSerializer
    queryset = Load.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.",
                LoadCreateRetrieveSerializer,
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
        IsAppUser,
    ]
    queryset = Contact.objects.all()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.", ContactListSerializer
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
                "Return the created contact object.", ContactCreateSerializer
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
            contact = User.objects.get(username=request.data["contact"])
        except User.DoesNotExist as e:
            return Response(
                {"details": ["User does not exist."]}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            contact = AppUser.objects.get(user=contact)
            request.data["contact"] = str(contact.id)
            if request.data["contact"] == request.data["origin"]:
                return Response(
                    {"details": ["Oops, you cannot add yourself!"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
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

    # override
    def perform_create(self, serializer):
        conatct = serializer.save()
        app_user = AppUser.objects.get(id=conatct.contact.id)
        origin_user = User.objects.get(id=app_user.user.id)
        contact_app_user = AppUser.objects.get(user=conatct.origin.id)
        Contact.objects.create(origin=origin_user, contact=contact_app_user)

    # override
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


class LoadFacilityView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]
    serializer_class = FacilityFilterSerializer
    queryset = Facility.objects.all()

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
                "Return the facility name, state and city.", FacilityFilterSerializer
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
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        keyword = ""
        if "keyword" in self.request.data:
            keyword = self.request.data["keyword"]
        if "shipper" in self.request.data:
            username = self.request.data["shipper"]
            try:
                shipper = User.objects.get(username=username)
                queryset = Facility.objects.filter(
                    owner=shipper.id, building_name__icontains=keyword
                ).order_by("building_name")
            except User.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
                queryset = []
        elif "consignee" in self.request.data:
            username = self.request.data["consignee"]
            try:
                consignee = User.objects.get(username=username)
                queryset = Facility.objects.filter(
                    owner=consignee.id, building_name__icontains=keyword
                ).order_by("building_name")
            except User.DoesNotExist as e:
                print(f"Unexpected {e=}, {type(e)=}")
                queryset = []
        else:
            queryset = []

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class ContactLoadView(GenericAPIView, ListModelMixin):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]
    serializer_class = ContactListSerializer
    queryset = Contact.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "keyword": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                "Return the contact list of a specific type.", ContactListSerializer
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

    def get_queryset(self):

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        if "type" in self.request.data:
            user_type = self.request.data["type"]
            keyword = ""
            if "keyword" in self.request.data:
                keyword = self.request.data["keyword"]
            queryset = Contact.objects.filter(
                origin=self.request.user.id,
                contact__user_type=user_type,
                contact__user__username__icontains=keyword,
            )
        else:
            queryset = []
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class ShipmentView(
    GenericAPIView,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
):

    permission_classes = [
        IsAuthenticated,
        IsShipmentPartyOrBroker,
    ]
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Returns a list of shipments.", ShipmentSerializer),
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
                ShipmentSerializer,
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
                ShipmentSerializer,
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
            update a shipment by changing the user who created this shipment or changing the shipments name or status

            **Example**
            >>> "created_by": "username#00000"
        """
        return self.partial_update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        app_user = AppUser.objects.get(user=request.user.id)

        if str(instance.created_by) == app_user.user.username:
            return Response(serializer.data)
        else:
            return Response(
                {
                    "detail": [
                        "You are not the creator of this Load",
                    ]
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        app_user = AppUser.objects.get(user=self.request.user.id)
        queryset = Shipment.objects.filter(created_by=app_user.id)

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = AppUser.objects.get(user=request.user)
        request.data["created_by"] = str(app_user.id)
        request.data["status"] = "Created"
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class OfferView(GenericAPIView, CreateModelMixin, ListModelMixin, UpdateModelMixin):
    def get(self, request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):

        return self.partial_update(request, *args, **kwargs)
