# Python imports
import uuid
from psycopg2 import IntegrityError

# Module imports
import authentication.models as models
import shipment.utilities as ship_utils
import authentication.utilities as utils
import shipment.models as ship_models
import authentication.serializers as serializers
import shipment.serializers as ship_serializers
import authentication.permissions as permissions

# Django imports
from django.http import QueryDict
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
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

SHIPMENT_PARTY = "shipment party"


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

            Create an AppUser with its according role form **(Dispatcher, Carrier, ShipmentParty)**

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
            200: openapi.Response("App user exists.", serializers.AppUserSerializer),
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
        app_user = models.AppUser.objects.get(user=request.user)

        tax_info = ship_utils.get_user_tax_or_company(app_user=app_user)
        if isinstance(tax_info, Response):
            return tax_info

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if "carrier" in app_user.user_type:

            res = utils.check_dot_number(dot_number=request.data["DOT_number"])
            if isinstance(res, Response):
                app_user.delete()
                return res

            elif res == True:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )

        else:
            return Response(
                {"user role": "User is not registered as a carrier"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DispatcherView(GenericAPIView, CreateModelMixin):

    permission_classes = [
        IsAuthenticated,
        permissions.IsAppUser,
    ]
    serializer_class = serializers.DispatcherSerializer
    queryset = models.Dispatcher.objects.all()

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
        app_user = models.AppUser.objects.get(user=request.user.id)

        tax_info = ship_utils.get_user_tax_or_company(app_user=app_user)
        if isinstance(tax_info, Response):
            return tax_info

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if "dispatcher" in app_user.user_type:

            res = utils.check_mc_number(mc_number=request.data["MC_number"])
            if isinstance(res, Response):
                app_user.delete()
                return res

            elif res == True:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )

        else:
            return Response(
                {"user role": "User is not registered as a dispatcher"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CompanyView(GenericAPIView, CreateModelMixin):

    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.CompanySerializer
    queryset = models.Company.objects.all()

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Company retrieved",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company ID"
                        ),
                        "name": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company name"
                        ),
                        "address": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Address ID"
                        ),
                        "EIN": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Employer Identification Number",
                        ),
                    },
                ),
            ),
            404: "Company not found.",
            500: "Internal server error.",
        }
    )
    def get(self, request, *args, **kwargs):
        app_user = models.AppUser.objects.get(user=request.user)
        company_employee = get_object_or_404(models.CompanyEmployee, app_user=app_user)
        company = get_object_or_404(models.Company, id=company_employee.company.id)

        return Response(
            status=status.HTTP_200_OK, data=serializers.CompanySerializer(company).data
        )

    @swagger_auto_schema(
        request_body=serializers.CompanySerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Company created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company ID"
                        ),
                        "name": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company name"
                        ),
                        "address": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Address ID"
                        ),
                        "EIN": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Employer Identification Number",
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Address creation failed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "details": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        address = None
        company_employee = None
        company = None
        try:
            app_user = models.AppUser.objects.get(user=request.user)

            address = utils.create_address(
                created_by=app_user,
                address=request.data["address"],
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
                request.data["address"],
                request.data["city"],
                request.data["state"],
                request.data["country"],
                request.data["zip_code"],
            )
            request.data["address"] = str(address.id)
            request.data["identifier"] = utils.generate_company_identiefier()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company = self.perform_create(serializer)
            app_user = models.AppUser.objects.get(user=request.user)
            company_employee = models.CompanyEmployee.objects.create(
                app_user=app_user, company=company
            )
            company_employee.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            if "first" in request.data and request.data["first"] == True:
                return self._handle_first_error(
                    app_user, address, company, company_employee, e
                )
            else:
                return self._handle_basic_error(company, company_employee, address, e)

    # override
    def perform_create(self, serializer):
        instance = serializer.save()
        return instance

    def _handle_first_error(
        self,
        app_user: models.AppUser,
        address: ship_models.Address,
        company: models.Company,
        company_employee: models.CompanyEmployee,
        e,
    ):
        if company:
            company.delete()
        if company_employee:
            company_employee.delete()
        if address:
            address.delete()
        app_user.delete()
        if isinstance(e, IntegrityError):
            return Response(
                {"details": "A company with this name already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                {"details": "An error occurred during company creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_basic_error(
        self,
        company: models.Company,
        company_employee: models.AppUser,
        address: ship_models.Address,
        e,
    ):
        if company:
            company.delete()
        if company_employee:
            company_employee.delete()
        if address:
            address.delete()
        if isinstance(e, IntegrityError):
            return Response(
                {"details": "A company with this name already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                {"details": "An error occurred during company creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserTaxView(GenericAPIView, CreateModelMixin):

    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.UserTaxSerializer
    queryset = models.UserTax.objects.all()

    @swagger_auto_schema(
        responses={
            200: serializers.UserTaxSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
    )
    def get(self, request, *args, **kwargs):
        if "tin" in request.query_params:
            tin = request.query_params["tin"]
            try:
                models.UserTax.objects.get(TIN=tin)
                app_user = models.AppUser.objects.get(user=request.user)
                app_user.delete()
                return Response(
                    [{"details": "Invalid Tax Identification Number"}],
                    status=status.HTTP_409_CONFLICT,
                )
            except models.UserTax.DoesNotExist:
                return Response(
                    [{"details": "User tax identification number not found"}],
                    status=status.HTTP_404_NOT_FOUND,
                )
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                app_user = models.AppUser.objects.get(user=request.user)
                app_user.delete()
                return Response(
                    {"details": "U-T"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            app_user = get_object_or_404(models.AppUser, user=request.user)
            user_tax = get_object_or_404(models.UserTax, app_user=app_user)
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.UserTaxSerializer(user_tax).data,
            )

    @swagger_auto_schema(
        request_body=serializers.UserTaxSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="User tax created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="User tax ID"
                        ),
                        "app_user": openapi.Schema(
                            type=openapi.TYPE_STRING, description="App user ID"
                        ),
                        "tax_id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Tax ID"
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="User tax creation failed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "details": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="either tax_id or app_user is missing",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        address = None

        try:
            app_user = models.AppUser.objects.get(user=request.user)

            address = utils.create_address(
                created_by=app_user,
                address=request.data["address"],
                city=request.data["city"],
                state=request.data["state"],
                country=request.data["country"],
                zip_code=request.data["zip_code"],
            )

            if address == False:
                return Response(
                    [
                        {
                            "details": "Address creation failed. Please try again; if the issue persists please contact us."
                        },
                    ],
                    status=status.HTTP_400_BAD_REQUEST,
                )

            del (
                request.data["address"],
                request.data["city"],
                request.data["state"],
                request.data["country"],
                request.data["zip_code"],
            )
            request.data["address"] = str(address.id)

            app_user = models.AppUser.objects.get(user=request.user)
            request.data["app_user"] = str(app_user.id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            if "first" in request.data and request.data["first"] == True:
                return self._handle_first_error(app_user, address)
            else:
                return self._handle_basic_error(address)

    def _handle_first_error(
        self, app_user: models.AppUser, address: ship_models.Address
    ):
        if address:
            address.delete()
        app_user.delete()
        return Response(
            {"details": "An error occurred during user tax creation."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def _handle_basic_error(self, address: ship_models.Address):
        if address:
            address.delete()
        return Response(
            {"details": "An error occurred during user tax creation."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class CompanyEmployeeView(GenericAPIView, CreateModelMixin):

    permission_classes = [IsAuthenticated, permissions.HasRole]
    serializer_class = serializers.CompanyEmployeeSerializer
    queryset = models.CompanyEmployee.objects.all()

    @swagger_auto_schema(
        operation_description="Get company employee",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Company employee",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company employee ID"
                        ),
                        "company": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company ID"
                        ),
                        "app_user": openapi.Schema(
                            type=openapi.TYPE_STRING, description="App user ID"
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Company employee not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "details": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                    },
                ),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """Get company employee"""
        if "ein" in request.query_params:
            ein = request.query_params.get("ein")
            company = get_object_or_404(models.Company, EIN=ein)
            company_employees = models.CompanyEmployee.objects.filter(
                company=company
            ).values_list("app_user", flat=True)
            app_users = models.AppUser.objects.filter(id__in=company_employees)
            data = {
                "company": serializers.CompanySerializer(company).data,
                "employees": serializers.AppUserSerializer(app_users, many=True).data,
            }

            return Response(status=status.HTTP_200_OK, data=data)
        if "au-id" in request.query_params:
            app_user_id = request.query_params.get("au-id")
            company_employee = get_object_or_404(
                models.CompanyEmployee, app_user=app_user_id
            )
            company = get_object_or_404(models.Company, id=company_employee.company.id)

            return Response(
                status=status.HTTP_200_OK,
                data=serializers.CompanySerializer(company).data,
            )
        else:
            return Response(
                [
                    {
                        "details": "Please provide either ein or au-id in the query params"
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_description="Create a company employee",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "company": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Company ID"
                ),
                "app_user": openapi.Schema(
                    type=openapi.TYPE_STRING, description="App User ID"
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Company employee created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "company": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Company ID"
                        ),
                        "app_user": openapi.Schema(
                            type=openapi.TYPE_STRING, description="App User ID"
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Company employee creation failed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "details": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="either company or app user is missing",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)

    # override
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        app_user = models.AppUser.objects.get(user=request.user)
        request.data["app_user"] = str(app_user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CheckCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if "ein" in request.query_params:
            ein = request.query_params.get("ein")
            company = get_object_or_404(models.Company, EIN=ein)

            return Response(
                status=status.HTTP_200_OK,
                data=serializers.CompanySerializer(company).data,
            )


class TaxInfoView(APIView):
    @swagger_auto_schema(
        operation_description="Get tax info",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Tax info",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "type": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Tax info type"
                        ),
                    },
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Tax info not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "details": openapi.Schema(
                            type=openapi.TYPE_STRING, description="No tax info found"
                        ),
                    },
                ),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        app_user = ship_utils.get_app_user_by_username(username=request.user.username)
        res = ship_utils.get_user_tax_or_company(app_user=app_user)
        if isinstance(res, Response):
            return res

        if isinstance(res, models.Company):
            return Response(
                status=status.HTTP_200_OK,
                data={
                    "type": "company",
                    "company": serializers.CompanySerializer(res).data,
                },
            )

        if isinstance(res, models.UserTax):
            return Response(
                status=status.HTTP_200_OK,
                data={
                    "type": "individual",
                    "user_tax": serializers.UserTaxSerializer(res).data,
                },
            )


class AddRoleView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["type"],
            properties={
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "dot_number": openapi.Schema(type=openapi.TYPE_STRING),
                "mc_number": openapi.Schema(type=openapi.TYPE_STRING),
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

        app_user = models.AppUser.objects.get(user=request.user)
        new_type = request.data.get("type")

        if new_type is None or new_type not in [
            "carrier",
            SHIPMENT_PARTY,
            "dispatcher",
        ]:
            return Response(
                [{"details": "type field is required or invalid type"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if new_type == "carrier" and "carrier" not in app_user.user_type:
                composed_type = self._create_carrier(app_user=app_user, request=request)
                if isinstance(composed_type, Response):
                    return composed_type

            elif (
                new_type == SHIPMENT_PARTY and SHIPMENT_PARTY not in app_user.user_type
            ):
                sort_roles = app_user.user_type.split("-")
                sort_roles.append("shipment party")
                sort_roles.sort()
                composed_type = "-".join(sort_roles)
                shipment_party = models.ShipmentParty.objects.create(app_user=app_user)
                shipment_party.save()

            elif new_type == "dispatcher" and "dispatcher" not in app_user.user_type:
                composed_type = self._create_dispatcher(
                    app_user=app_user, request=request
                )
                if isinstance(composed_type, Response):
                    return composed_type

            else:
                return Response(
                    [{"details": "type already exists"}],
                    status=status.HTTP_400_BAD_REQUEST,
                )

            app_user.user_type = composed_type
            app_user.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializers.AppUserSerializer(app_user).data,
            )

        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            app_user.delete()
            return Response(
                {"details": "something went wrong - ADRL."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_carrier(self, request, app_user: models.AppUser):
        tax_info = ship_utils.get_user_tax_or_company(app_user=app_user)
        if isinstance(tax_info, Response):
            return tax_info
        sort_roles = app_user.user_type.split("-")
        sort_roles.append("carrier")
        sort_roles.sort()
        composed_type = "-".join(sort_roles)
        if "dot_number" not in request.data:
            return Response(
                [{"details": "dot number is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        res = utils.check_dot_number(dot_number=request.data["dot_number"])
        if isinstance(res, Response):
            return res

        if res:
            carrier = models.Carrier.objects.create(
                app_user=app_user,
                DOT_number=request.data["dot_number"],
                allowed_to_operate=True,
            )
            carrier.save()
            return composed_type

    def _create_dispatcher(self, request, app_user: models.AppUser):
        tax_info = ship_utils.get_user_tax_or_company(app_user=app_user)
        if isinstance(tax_info, Response):
            return tax_info
        sort_roles = app_user.user_type.split("-")
        sort_roles.append("dispatcher")
        sort_roles.sort()
        composed_type = "-".join(sort_roles)
        if "mc_number" not in request.data:
            return Response(
                [{"details": "mc number is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        res = utils.check_mc_number(mc_number=request.data["mc_number"])
        if isinstance(res, Response):
            return res

        if res:
            dispatcher = models.Dispatcher.objects.create(
                app_user=app_user,
                MC_number=request.data["mc_number"],
                allowed_to_operate=True,
            )
            dispatcher.save()
            return composed_type


class SelectRoleView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]

    def put(self, request, *args, **kwargs):
        app_user = models.AppUser.objects.get(user=request.user)
        if "type" not in request.data:
            return Response(
                [{"details": "type field is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_type = request.data.get("type")
        if new_type is None or new_type not in app_user.user_type:
            return Response(
                [{"details": "type field is required or invalid type"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        app_user.selected_role = new_type
        app_user.save()
        return Response(
            status=status.HTTP_200_OK, data=serializers.AppUserSerializer(app_user).data
        )


class InvitationsHandlingView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.InvitationsSerializer
    queryset = models.Invitation.objects.all()

    def get(self, request, *args, **kwargs):
        if "token" in request.query_params:
            token = request.query_params["token"]
            invitation = get_object_or_404(models.Invitation, token=token)
            invitee = User.objects.get(email=invitation.invitee)
            if invitee != request.user:
                return Response(
                    [{"details": "you are not the invitee"}],
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.InvitationsSerializer(invitation).data,
            )

        else:
            invitations = models.Invitation.objects.filter(inviter=request.user)
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.InvitationsSerializer(invitations, many=True).data,
            )

    def post(self, request, *args, **kwargs):
        if "token" not in request.data:
            return Response(
                [{"details": "token field is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = request.data["token"]
        invitation = get_object_or_404(models.Invitation, token=token)
        if invitation.inviter != request.user and invitation.invitee != request.user:
            return Response(
                [{"details": "you do not have access to this resource."}],
                status=status.HTTP_403_FORBIDDEN,
            )
        inviter_user = User.objects.get(id=invitation.invitee.id)
        invitee_user = User.objects.get(email=invitation.invitee)
        inviter_app_user = models.AppUser.objects.get(user=inviter_user)
        invitee_app_user = models.AppUser.objects.get(user=invitee_user)
        iniviter_contact = ship_models.Contact.objects.create(
            origin=inviter_user, contact=invitee_app_user
        )
        invitee_contact = ship_models.Contact.objects.create(
            origin=invitee_user, contact=inviter_app_user
        )
        data = {
            "inviter": ship_serializers.ContactCreateSerializer(iniviter_contact).data,
            "invitee": ship_serializers.ContactCreateSerializer(invitee_contact).data,
        }
        invitation.delete()
        return Response(status=status.HTTP_201_CREATED, data=data)


class CreateInvitationView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.InvitationsSerializer
    queryset = models.Invitation.objects.all()

    def post(self, request, *args, **kwargs):
        if "email" not in request.data:
            return Response(
                [{"details": "invitee field is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitee_email = request.data["email"]
        token = uuid.uuid4()
        invitation = models.Invitation.objects.create(
            inviter=request.user, invitee=invitee_email, token=token
        )
        invitation.save()
        # remaining code to send email including the signup URL with the token attached to it
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializers.InvitationsSerializer(invitation).data,
        )
