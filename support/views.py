import random
import string

# Django imports
from django.http import QueryDict
from django.core.exceptions import ValidationError

# Module imports
from support.models import Ticket
import shipment.models as ship_models
import support.serializers as serializers
import authentication.models as auth_models
import authentication.utilities as auth_utils
import authentication.permissions as permissions
import authentication.serializers as auth_serializers

# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)

# Third Party imports
from drf_spectacular.utils import extend_schema, OpenApiTypes, inline_serializer


class CompanyView(GenericAPIView, CreateModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsSupport]
    serializer_class = auth_serializers.CompanySerializer
    queryset = auth_models.Company.objects.all()

    @extend_schema(
        description="Create a Company.",
        request=inline_serializer(
            name="CompanyCreate",
            fields={
                "name": OpenApiTypes.STR,
                "address": OpenApiTypes.STR,
                "city": OpenApiTypes.STR,
                "state": OpenApiTypes.STR,
                "country": OpenApiTypes.STR,
                "zip_code": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_201_CREATED: auth_serializers.CompanySerializer,
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
            app_user = auth_models.AppUser.objects.get(user=request.user)

            address = auth_utils.create_address(
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
            request.data["identifier"] = auth_utils.generate_company_identiefier()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company = self.perform_create(serializer)
            app_user = auth_models.AppUser.objects.get(user=request.user)
            company_employee = auth_models.CompanyEmployee.objects.create(
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
        app_user: auth_models.AppUser,
        address: ship_models.Address,
        company: auth_models.Company,
        company_employee: auth_models.CompanyEmployee,
        e,
    ):
        if company:
            company.delete()
        if company_employee:
            company_employee.delete()
        if address:
            address.delete()
        app_user.delete()
        if isinstance(e, ValidationError):
            return Response(
                {"details": "company with this name already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                {"details": "An error occurred during company creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_basic_error(
        self,
        company: auth_models.Company,
        company_employee: auth_models.AppUser,
        address: auth_models.Address,
        e,
    ):
        if company:
            company.delete()
        if company_employee:
            company_employee.delete()
        if address:
            address.delete()
        if isinstance(e, ValidationError):
            return Response(
                {"details": "A company with this name already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return Response(
                {"details": "An error occurred during company creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RetrieveTicketView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    """
    View for Retrieving the Tickets
    """

    permission_classes = [IsAuthenticated, permissions.IsSupport]
    queryset = Ticket.objects.all()
    serializer_class = serializers.ListTicketsSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ListTicketsView(GenericAPIView, ListModelMixin):
    """
    View for Listing the Tickets
    """

    permission_classes = [IsAuthenticated, permissions.IsSupport]
    queryset = Ticket.objects.all()
    serializer_class = serializers.ListTicketsSerializer

    @extend_schema(
        description="List all Tickets.",
        responses={200: serializers.ListTicketsSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CreateTicketView(GenericAPIView, CreateModelMixin):
    """
    View for Creating the Tickets
    """

    queryset = Ticket.objects.all()
    serializer_class = serializers.CreateTicketSerializer

    @extend_schema(
        description="Create a Ticket.",
        request=serializers.CreateTicketSerializer,
        responses={200: serializers.CreateTicketSerializer},
    )
    def post(self, request, *args, **kwargs):
        """
        Create a Ticket.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(request.data)


class HandleTicketView(GenericAPIView, UpdateModelMixin):
    """
    View for Handling the Tickets
    """

    permissions_classes = [IsAuthenticated, permissions.IsSupport]
    queryset = Ticket.objects.all()
    serializer_class = serializers.ListTicketsSerializer
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(id=kwargs["id"])
        if ticket.status != "Pending":
            return Response(
                {"details": "Ticket has already been handled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data["action"] == "approve":
            # create an app user and a company using the informatrion in the ticket
            password = auth_utils.generate_password()
            username = (
                ticket.email.split("@")[0]
                + "#"
                + (
                    "".join(
                        random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(5)
                    )
                )
            )
            while auth_models.User.objects.filter(username=username).exists():
                username = (
                    ticket.email.split("@")[0]
                    + "#"
                    + (
                        "".join(
                            random.choice(string.ascii_uppercase + string.digits)
                            for _ in range(5)
                        )
                    )
                )

            user = auth_models.User.objects.create(
                email=ticket.email,
                password=password,
                username=username,
                first_name=ticket.first_name,
                last_name=ticket.last_name,
                is_active=True,
            )
            app_user = auth_models.AppUser.objects.create(
                user=user,
                phone_number=ticket.personal_phone_number,
                user_type="manager",
                selected_role="manager",
            )
            company_id = auth_utils.generate_company_identiefier()
            while auth_models.Company.objects.filter(identifier=company_id).exists():
                company_id = auth_utils.generate_company_identiefier()

            company = auth_models.Company.objects.create(
                name=ticket.company_name,
                address=ticket.company_address,
                identifier=auth_utils.generate_company_identiefier(),
                EIN=ticket.EIN,
                fax_number=ticket.company_fax_number,
                phone_number=ticket.company_phone_number,
                admin=app_user,
            )
            ticket.status = "Approved"
            ticket.save()
            return Response(
                {"details": "Ticket has been approved"},
                status=status.HTTP_200_OK,
                data={
                    "company": auth_serializers.CompanySerializer(company).data,
                    "app_user": auth_serializers.AppUserSerializer(app_user).data,
                },
            )
        elif request.data["action"] == "deny":
            if "rejection_reason" not in request.data:
                return Response(
                    {"details": "Reasoning is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ticket.status = "Denied"
            ticket.rejection_reason = request.data["rejection_reason"]
            ticket.save()
            return Response(
                {"details": "Ticket has been denied"},
                status=status.HTTP_200_OK,
                data={"ticket": serializers.ListTicketsSerializer(ticket).data},
            )
        else:
            return Response(
                {"details": "Action is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
