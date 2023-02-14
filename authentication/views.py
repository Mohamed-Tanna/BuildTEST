import os
import requests
# Module imports
import authentication.models as models
import authentication.serializers as serializers
import authentication.permissions as permissions
# Django imports
from django.http import QueryDict
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
# DRF imports
from rest_framework import status
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
# third party imports
from drf_yasg import openapi
from google.cloud import secretmanager
from drf_yasg.utils import swagger_auto_schema
from allauth.account.models import EmailAddress


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

    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = serializers.AppUserSerializer
    queryset = models.AppUser.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_type", "phone_number"],
            properties={
                "user_type": openapi.Schema(type=openapi.TYPE_STRING),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "Created",
            400: "Bad Request",
            403: "Email Address Is Not Verified",
            500: "Internal Server Error",
        },
    )
    def post(self, request, *args, **kwargs):

        """
        Create an AppUser from an existing user

            Create an AppUser with its according role form **(Broker, Carrier, ShipmentParty)**

            **Example**
                >>> user_type : shipment party
                >>> phone_number : +1 (123) 456-7890
        """

        user = request.user.id
        try:
            email_address = EmailAddress.objects.get(user=user)

            if email_address.verified == True:
                return self.create(request, *args, **kwargs)
            else:
                msg = gettext_lazy("email address is not verified")
                raise exceptions.NotAuthenticated(msg)

        except PermissionDenied as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(status=status.HTTP_403_FORBIDDEN, data=e.args[0])

        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.args[0])

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "App user exists.", serializers.AppUserSerializer
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        },
    )
    def get(self, request, *args, **kwargs):

        try:
            app_user = models.AppUser.objects.get(user=request.user)
            data = serializers.AppUserSerializer(app_user).data
            return Response(data=data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"detail": ["The requested app user does not exist"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        except (BaseException) as e:
            return Response(
                {"detail": [f"{e.args[0]}"]}, status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["user"] = str(request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class BaseUserView(GenericAPIView, UpdateModelMixin):

    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = serializers.BaseUserUpdateSerializer
    queryset = User.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
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

                >>> first_name: John
                >>> last_name: Doe
        """

        if self.kwargs["id"] == str(request.user.id):
            return self.partial_update(request, *args, **kwargs)
        else:
            return Response({"detail": ["Insufficient Permissions"]})


class ShipmentPartyView(GenericAPIView, CreateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsAppUser,
    ]
    serializer_class = serializers.ShipmentPartySerializer
    queryset = models.ShipmentParty.objects.all()
            
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
                >>> app_user: ""
        """

        return self.create(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):

        app_user = models.AppUser.objects.get(user=request.user)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CarrierView(GenericAPIView, CreateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsAppUser,
    ]
    serializer_class = serializers.CarrierSerializer
    queryset = models.Carrier.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["DOT_number"],
            properties={
                "DOT_number": openapi.Schema(type=openapi.TYPE_STRING),
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

        return self.create(request, *args, **kwargs)

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
        app_user = models.AppUser.objects.get(user=request.user)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if app_user.user_type == "carrier":
            dot_number = request.data.get("DOT_number")
            URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={webkey}"
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
                    raise exceptions.PermissionDenied(msg)

            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(status=status.HTTP_403_FORBIDDEN, data=e.args[0])
        else:
            return Response(
                {"user role": ["User is not registered as a carrier"]},
                status=status.HTTP_403_FORBIDDEN,
            )


class BrokerView(GenericAPIView, CreateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsAppUser,
    ]
    serializer_class = serializers.BrokerSerializer
    queryset = models.Broker.objects.all()

    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["MC_number"],
            properties={
                "MC_number": openapi.Schema(type=openapi.TYPE_STRING),
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

        return self.create(request, *args, **kwargs)

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
        app_user = models.AppUser.objects.get(user=request.user)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if app_user.user_type == "broker":
            mc_number = request.data.get("MC_number")
            URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={webkey}"
            try:
                res = requests.get(url=URL)
                data = res.json()
                allowed_to_operate = data["content"][0]["carrier"]["allowedToOperate"]

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
                    raise exceptions.PermissionDenied(msg)

            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(status=status.HTTP_403_FORBIDDEN, data=e.args[0])
        else:
            return Response(
                {"user role": ["User is not registered as a broker"]},
                status=status.HTTP_403_FORBIDDEN,
            )
