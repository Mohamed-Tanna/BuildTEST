import requests
import os
from google.cloud import secretmanager
from .models import AppUser, Carrier
from allauth.account.models import EmailAddress
from .serializers import *
from rest_framework import exceptions
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from shipment.models import Facility
from shipment.serializers import FacilitySerializer
from django.utils.translation import gettext_lazy


class HealthCheckView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="An endpoint created expressly to respond to health check requests"
            )
        }
    )
    def get(self, request, *args, **kwargs):

        return Response(status=status.HTTP_200_OK)


class AppUserView(GenericAPIView, CreateModelMixin):

    serializer_class = AppUserSerializer
    queryset = AppUser.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user", "user_type"],
            properties={
                "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                "user_type": openapi.Schema(type=openapi.TYPE_STRING),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "Created",
            500: "internal server error",
        },
    )
    def post(self, request, *args, **kwargs):

        """
        Create an AppUser from an existing user

        Create an AppUser with its according role form **(Broker, Carrier, ShipmentParty)**

        **Example**

            >>> user : 6
            >>> user_type : shipment party
            >>> phone_number : +1 (123) 456-1234
        """

        user = request.data.get("user")
        try:
            email_address = EmailAddress.objects.get(user=user)
            if email_address.verified == True:
                return self.create(request, *args, **kwargs)
            else:
                msg = gettext_lazy("email address is not verified")
                raise exceptions.NotAuthenticated(msg=msg)
        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=e.args[0])


class BaseUserView(GenericAPIView, UpdateModelMixin):

    serializer_class = BaseUserUpdateSerializer
    queryset = User.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: "OK",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def put(self, request, *args, **kwargs):

        """
        Update username, first name and last name

        Update the base user **username**, **first name** and **last name** either separately or coupled all together

        **Example**

            >>> username: JohnDoe
            >>> first_name: John
            >>> last_name: Doe
        """

        return self.update(request, *args, **kwargs)


class ShipmentPartyView(GenericAPIView, CreateModelMixin):

    serializer_class = ShipmentPartySerializer

    # override
    def create(self, request, *args, **kwargs):
        user = request.data.get("app_user")
        app_user = AppUser.objects.get(id=user)
        if app_user.user_type == "shipment party":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["app_user"],
            properties={
                "app_user": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "CREATED",
            400: "BAD REQUEST",
            404: "NOT FOUND",
            500: "INTERNAL SERVER ERROR",
        },
    )
    def post(self, request, *args, **kwargs):

        """
        Create a Shipment Party from an existing App User

        Create a **Shipment Party** with all the role's additional data - if any - and verify them if required

        **Example**

            >>> app_user: 4
        """

        return self.create(request, *args, **kwargs)


class FacilityView(GenericAPIView, CreateModelMixin):

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
        )
    )
    def post(self, request, *args, **kwargs):

        """
        Create a Facility

        Create a **Facility** with an existing **Shipment Party** as its owner

        **Example**
            >>> facility: {facility: facility_object}
        """

        return self.create(request, *args, **kwargs)


class CarrierView(GenericAPIView, CreateModelMixin):

    serializer_class = CarrierSerializer
    queryset = Carrier.objects.all()

    # override
    def perform_create(self, serializer):
        carrier = serializer.save()
        carrier.allowed_to_operate = True
        carrier.save()

    # override
    def create(self, request, *args, **kwargs):

        client = secretmanager.SecretManagerServiceClient()
        webkey = client.access_secret_version(
            request={
                "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('FMCSA_WEBKEY')}/versions/1"
            }
        )
        webkey = webkey.payload.data.decode("UTF-8")
        app_user = request.data.get("app_user")
        app_user = AppUser.objects.get(id=app_user)
        if app_user.user_type == "carrier":
            DOT_number = request.data.get("DOT_number")
            URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{DOT_number}?webKey={webkey}"
            try:
                res = requests.get(url=URL)
                data = res.json()
                allowed_to_operate = data["content"]["carrier"]["allowedToOperate"]

                if allowed_to_operate == "Y":
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED, headers=headers
                    )

                else:
                    msg = gettext_lazy(
                        "Carrier is not allowed to operate, if you think this is a mistake please contact the FMCSA"
                    )
                    raise exceptions.PermissionDenied(msg=msg)

            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(status=status.HTTP_403_FORBIDDEN, data=e.args[0])
        else:
            return Response(
                {"user role": ["User is not registered as a carrier"]},
                status=status.HTTP_403_FORBIDDEN,
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["app_user", "DOT_number"],
            properties={
                "app_user": openapi.Schema(type=openapi.TYPE_STRING),
                "DOT_number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
    )
    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)


class BrokerView(GenericAPIView, CreateModelMixin):

    serializer_class = BrokerSerializer
    queryset = Broker.objects.all()

    # override
    def perform_create(self, serializer):
        carrier = serializer.save()
        carrier.allowed_to_operate = True
        carrier.save()

    # override
    def create(self, request, *args, **kwargs):

        client = secretmanager.SecretManagerServiceClient()
        webkey = client.access_secret_version(
            request={
                "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('FMCSA_WEBKEY')}/versions/1"
            }
        )
        webkey = webkey.payload.data.decode("UTF-8")
        app_user = request.data.get("app_user")
        app_user = AppUser.objects.get(id=app_user)
        if app_user.user_type == "broker":
            MC_number = request.data.get("MC_number")
            URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{MC_number}?webKey={webkey}"
            try:
                res = requests.get(url=URL)
                data = res.json()
                allowed_to_operate = data["content"]["carrier"]["allowedToOperate"]

                if allowed_to_operate == "Y":
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED, headers=headers
                    )

                else:
                    msg = gettext_lazy(
                        "Broker is not allowed to operate, if you think this is a mistake please contact the FMCSA"
                    )
                    raise exceptions.PermissionDenied(msg=msg)

            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(status=status.HTTP_403_FORBIDDEN, data=e.args[0])
        else:
            return Response(
                {"user role": ["User is not registered as a broker"]},
                status=status.HTTP_403_FORBIDDEN,
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["app_user", "MC_number"],
            properties={
                "app_user": openapi.Schema(type=openapi.TYPE_STRING),
                "MC_number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
    )
    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)