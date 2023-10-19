# Module imports
import authentication.models as models
import shipment.utilities as ship_utils
import authentication.utilities as utils
import shipment.models as ship_models
import authentication.serializers as serializers
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
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin

# third party imports
from allauth.account.models import EmailAddress
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer


SHIPMENT_PARTY = "shipment party"


class HealthCheckView(APIView):
    @extend_schema(description="Health check endpoint.", responses={200: "OK"})
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class AppUserView(GenericAPIView, CreateModelMixin):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = serializers.AppUserSerializer
    queryset = models.AppUser.objects.all()

    @extend_schema(
        description="Create an AppUser from an existing user.",
        request=inline_serializer(
            name="AppUserCreate",
            fields={
                "user_type": OpenApiTypes.STR,
                "phone_number": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.AppUserSerializer,
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

        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.args[0])

    @extend_schema(
        description="Get an AppUser from an existing user.",
        responses={
            status.HTTP_200_OK: serializers.AppUserSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve an AppUser from an existing user
        """

        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return Response(
                data=serializers.AppUserSerializer(app_user).data,
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(
                {"detail": ["The requested app user does not exist"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        except BaseException as e:
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

    @extend_schema(
        description="Update username, first name and last name.",
        request=inline_serializer(
            name="BaseUserUpdate",
            fields={
                "username": OpenApiTypes.STR,
                "first_name": OpenApiTypes.STR,
                "last_name": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_200_OK: serializers.BaseUserUpdateSerializer,
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

    @extend_schema(
        description="Create a Shipment Party from an existing App User.",
        request=inline_serializer(
            name="ShipmentPartyCreate",
            fields={
                "app_user": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.ShipmentPartySerializer,
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

    @extend_schema(
        description="Create a Carrier from an existing App User.",
        request=inline_serializer(
            name="CarrierCreate",
            fields={
                "app_user": OpenApiTypes.STR,
                "DOT_number": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.CarrierSerializer,
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

        ship_utils.get_user_tax_or_company(app_user=app_user)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if "carrier" in app_user.user_type:

            try:
                utils.check_dot_number(dot_number=request.data["DOT_number"])
            except (exceptions.ParseError, exceptions.NotFound, exceptions.PermissionDenied) as e:
                app_user.delete()
                raise e

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

    @extend_schema(
        description="Create a Dispatcher from an existing App User.",
        request=inline_serializer(
            name="DispatcherCreate",
            fields={
                "app_user": OpenApiTypes.STR,
                "MC_number": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.DispatcherSerializer,
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

        try:
            ship_utils.get_user_tax_or_company(app_user=app_user)
        except exceptions.NotFound:
            app_user.delete()

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["app_user"] = str(app_user.id)

        if "dispatcher" in app_user.user_type:
            try:
                utils.check_mc_number(mc_number=request.data["MC_number"])
            except (exceptions.ParseError, exceptions.NotFound, exceptions.PermissionDenied) as e:
                app_user.delete()
                raise e

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

    @extend_schema(
        description="Retrieve a Company.",
        responses={
            status.HTTP_201_CREATED: serializers.CompanySerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        app_user = models.AppUser.objects.get(user=request.user)
        company_employee = get_object_or_404(
            models.CompanyEmployee, app_user=app_user)
        company = get_object_or_404(
            models.Company, id=company_employee.company.id)

        return Response(
            status=status.HTTP_200_OK, data=serializers.CompanySerializer(
                company).data
        )


class UserTaxView(GenericAPIView, CreateModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.UserTaxSerializer
    queryset = models.UserTax.objects.all()

    @extend_schema(
        description="Retrieve a User Tax.",
        responses={
            status.HTTP_200_OK: serializers.UserTaxSerializer,
        },
        parameters=[
            OpenApiParameter(
                name="tin",
                description="Tax Identification Number",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
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
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                app_user = models.AppUser.objects.get(user=request.user)
                app_user.delete()
                return Response(
                    {"details": "TIN"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            app_user = get_object_or_404(models.AppUser, user=request.user)
            user_tax = get_object_or_404(models.UserTax, app_user=app_user)
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.UserTaxSerializer(user_tax).data,
            )

    @extend_schema(
        description="Create a User Tax.",
        request=inline_serializer(
            name="UserTaxCreate",
            fields={
                "app_user": OpenApiTypes.STR,
                "TIN": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.UserTaxSerializer,
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
        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            if "first" in request.data and request.data["first"] == True:
                return self._handle_first_error(app_user, address, e)
            else:
                return self._handle_basic_error(address, e)

    def _handle_first_error(
        self, app_user: models.AppUser, address: ship_models.Address, e
    ):
        if address:
            address.delete()
        app_user.delete()
        if isinstance(e, ValidationError):
            return Response(
                {"details": "The TIN is invalid, kindly double check."},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                {"details": "An error occurred during user tax creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_basic_error(self, address: ship_models.Address, e):
        if address:
            address.delete()
        return Response(
            {"details": "An error occurred during user tax creation."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class CompanyEmployeeView(GenericAPIView, CreateModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.CompanyEmployeeSerializer
    queryset = models.CompanyEmployee.objects.all()

    @extend_schema(
        description="Retrieve a Company Employee.",
        responses={
            status.HTTP_201_CREATED: serializers.CompanyEmployeeSerializer,
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
            company = get_object_or_404(
                models.Company, id=company_employee.company.id)

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

    @extend_schema(
        description="Create a Company Employee.",
        request=inline_serializer(
            name="CompanyEmployeeCreate",
            fields={
                "app_user": OpenApiTypes.STR,
                "company": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.CompanyEmployeeSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CheckCompanyView(GenericAPIView, CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CompanyEmployeeSerializer
    queryset = models.CompanyEmployee.objects.all()

    @extend_schema(
        description="Check if a company exists.",
        responses={
            status.HTTP_200_OK: "means company exists",
            status.HTTP_404_NOT_FOUND: "means company does not exist",
        },
        parameters=[
            OpenApiParameter(
                name="id",
                description="Company unique id",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        if "domain" in request.query_params:
            domain = request.query_params.get("domain")
            company = get_object_or_404(models.Company, domain=domain)

            return Response(
                status=status.HTTP_200_OK,
                data=serializers.CompanySerializer(company).data,
            )

        elif "id" in request.query_params:
            identifier = request.query_params.get("id")
            company = get_object_or_404(models.Company, identifier=identifier)

            return Response(
                status=status.HTTP_200_OK,
                data=serializers.CompanySerializer(company).data,
            )

        else:
            return Response(
                [
                    {
                        "details": "Kindly provide the company's domain or the company's ID."
                    },
                ],
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        description="Create a Company Employee.",
        request=inline_serializer(
            name="CompanyEmployeeCreate",
            fields={
                "app_user": OpenApiTypes.STR,
                "company": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.CompanyEmployeeSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a Company Employee."""
        return self.create(request, *args, **kwargs)


class TaxInfoView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]

    @extend_schema(
        description="Get the tax information of a user.",
        responses={
            status.HTTP_200_OK: "user tax info exists",
            status.HTTP_404_NOT_FOUND: "user tax info does not exist",
        },
    )
    def get(self, request, *args, **kwargs):
        app_user = ship_utils.get_app_user_by_username(
            username=request.user.username)
        res = ship_utils.get_user_tax_or_company(app_user=app_user)

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
    permission_classes = [IsAuthenticated, permissions.IsAppUser]

    @extend_schema(
        description="Add a role to an existing App User.",
        request=inline_serializer(
            name="AddRole",
            fields={
                "type": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: serializers.AppUserSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        app_user = models.AppUser.objects.get(user=request.user)
        new_type = request.data.get("type", None)

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
                composed_type = self._create_carrier(
                    app_user=app_user, request=request)

            elif (
                new_type == SHIPMENT_PARTY and SHIPMENT_PARTY not in app_user.user_type
            ):
                sort_roles = app_user.user_type.split("-")
                sort_roles.append("shipment party")
                sort_roles.sort()
                composed_type = "-".join(sort_roles)
                shipment_party = models.ShipmentParty.objects.create(
                    app_user=app_user)
                shipment_party.save()

            elif new_type == "dispatcher" and "dispatcher" not in app_user.user_type:
                composed_type = self._create_dispatcher(
                    app_user=app_user, request=request
                )

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

        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            app_user.delete()
            return Response(
                {"details": "something went wrong - ADRL."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_carrier(self, request, app_user: models.AppUser):
        ship_utils.get_user_tax_or_company(app_user=app_user)
        sort_roles = app_user.user_type.split("-")
        sort_roles.append("carrier")
        sort_roles.sort()
        composed_type = "-".join(sort_roles)
        if "dot_number" not in request.data:
            raise exceptions.ParseError("dot number is required")

        utils.check_dot_number(dot_number=request.data["dot_number"])

        carrier = models.Carrier.objects.create(
            app_user=app_user,
            DOT_number=request.data["dot_number"],
            allowed_to_operate=True,
        )
        carrier.save()
        return composed_type

    def _create_dispatcher(self, request, app_user: models.AppUser):
        ship_utils.get_user_tax_or_company(app_user=app_user)
        sort_roles = app_user.user_type.split("-")
        sort_roles.append("dispatcher")
        sort_roles.sort()
        composed_type = "-".join(sort_roles)
        if "mc_number" not in request.data:
            raise exceptions.ParseError("mc number is required")

        utils.check_mc_number(mc_number=request.data["mc_number"])

        dispatcher = models.Dispatcher.objects.create(
            app_user=app_user,
            MC_number=request.data["mc_number"],
            allowed_to_operate=True,
        )
        dispatcher.save()
        return composed_type


class SelectRoleView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]

    @extend_schema(
        description="Select a role for an existing App User.",
        request=inline_serializer(
            name="SelectRole",
            fields={
                "type": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_200_OK: serializers.AppUserSerializer,
        },
    )
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
            status=status.HTTP_200_OK, data=serializers.AppUserSerializer(
                app_user).data
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]

    @extend_schema(
        description="Change password.",
        request=inline_serializer(
            name="ChangePassword",
            fields={
                "old_password": OpenApiTypes.STR,
                "new_password": OpenApiTypes.STR,
                "confirm_password": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_200_OK: "Password changed successfully",
        },
    )
    def put(self, request, *args, **kwargs):
        if "old_password" not in request.data or "new_password" not in request.data:
            return Response(
                {"details": "old password and new password fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["old_password"] == request.data["new_password"]:
            return Response(
                {"details": "old password and new password cannot be the same"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["new_password"] != request.data["confirm_password"]:
            return Response(
                {"details": "new password and confirm password do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.check_password(request.data["old_password"]):
            return Response(
                {"details": "old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(request.data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_200_OK)
