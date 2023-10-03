import random
import string

# Module imports
import support.utilities as utils
from support.models import Ticket
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


class RetrieveTicketView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    """
    View for Retrieving the Tickets
    """

    permission_classes = [IsAuthenticated, permissions.IsSupport]
    queryset = Ticket.objects.all()
    serializer_class = serializers.RetrieveTicketSerializer
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
            utils.send_request_result(
                template="accepted_request.html",
                to=ticket.email,
                password_or_reason=password,
                company_name=ticket.company_name,
                subject="Congratulations! Your Company Request Has Been Approved",
            )
            return Response(
                {
                    "details": "Ticket has been approved",
                    "company": auth_serializers.CompanySerializer(company).data,
                    "app_user": auth_serializers.AppUserSerializer(app_user).data,
                },
                status=status.HTTP_200_OK,
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
            utils.send_request_result(
                template="denied_request.html",
                to=ticket.email,
                password_or_reason=ticket.rejection_reason,
                company_name=ticket.company_name,
                subject="Your Company Request Has Been Denied",
            )
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
