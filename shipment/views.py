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
    DestroyModelMixin,
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
        request_body=LoadCreateRetrieveSerializer,
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
            try:
                shipper = User.objects.get(username=username)
                shipper = AppUser.objects.get(user=shipper.id)
                shipper = ShipmentParty.objects.get(app_user=shipper.id)
                request.data["shipper"] = str(shipper.id)
            except User.DoesNotExist:
                return Response(
                    {"detail": ["shipper does not exist."]},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(
                    {"detail": ["This user is not a shipper."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"detail": ["shipper is requried."]}, status=status.HTTP_400_BAD_REQUEST
            )

        if "consignee" in request.data:
            username = request.data["consignee"]
            try:
                consignee = User.objects.get(username=username)
                consignee = AppUser.objects.get(user=consignee.id)
                consignee = ShipmentParty.objects.get(app_user=consignee.id)
                request.data["consignee"] = str(consignee.id)
            except User.DoesNotExist:
                return Response(
                    {"detail": ["consignee does not exist."]},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(
                    {"detail": ["This user is not a consignee."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"detail": ["consignee is requried."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "broker" in request.data:
            username = request.data["broker"]
            try:
                broker = User.objects.get(username=username)
                broker = AppUser.objects.get(user=broker.id)
                broker = Broker.objects.get(app_user=broker.id)
                request.data["broker"] = str(broker.id)
            except User.DoesNotExist:
                return Response(
                    {"detail": ["broker does not exist."]},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(
                    {"detail": ["This user is not broker."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")

            if "delivery_date_check" in str(
                e.__cause__
            ) or "pick_up_date should be greater than or equal today's date" in str(
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

            elif "pick up location and drop off location cannot be equal" in str(
                e.__cause__
            ):
                return Response(
                    {
                        "detail": [
                            "pick up location and drop off location cannot be equal, please double check the dates and try again"
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

        queryset = Load.objects.filter(filter_query)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

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
