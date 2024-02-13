import random
import re
import string

from django.db import IntegrityError

# Module imports
import manager.models as manager_models
import support.utilities as utils
from shipment.models import Claim
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
from drf_spectacular.utils import extend_schema
from allauth.account.models import EmailAddress


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
    queryset = Ticket.objects.all().order_by("-id")
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
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = serializers.CreateTicketSerializer

    @extend_schema(
        description="Create a Ticket.",
        request=serializers.CreateTicketSerializer,
        responses={200: serializers.CreateTicketSerializer},
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        mutable_request_data = request.data.copy()
        app_user = auth_models.AppUser.objects.get(user=request.user.id)
        check_result = self.check_if_user_can_create_ticket(app_user)
        if not check_result["isAllowed"]:
            return Response(
                {
                    "details": check_result["message"]
                },
                status=status.HTTP_403_FORBIDDEN
            )
        mutable_request_data["email"] = app_user.user.email
        mutable_request_data["first_name"] = app_user.user.first_name
        mutable_request_data["last_name"] = app_user.user.last_name
        mutable_request_data["personal_phone_number"] = app_user.phone_number
        serializer = self.get_serializer(data=mutable_request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            error_message = str(e)
            error_info = utils.extract_integrity_error_info(error_message)
            return Response(
                {error_info["column_name"]: error_info['message']},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def check_if_user_can_create_ticket(app_user: auth_models.AppUser):
        result = {"isAllowed": True, "message": ""}
        if len(Ticket.objects.filter(email=app_user.user.email)) > 0:
            result["isAllowed"] = False
            result["message"] = "You already submitted a ticket"
        elif len(auth_models.Company.objects.filter(manager=app_user)) > 0:
            result["isAllowed"] = False
            result["message"] = "You already have a company"
        return result


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
            user = auth_models.User.objects.get(email=ticket.email)
            app_user = auth_models.AppUser.objects.get(user=user)

            address = auth_utils.create_address(
                address=ticket.address,
                city=ticket.city,
                state=ticket.state,
                country=ticket.country,
                zip_code=ticket.zip_code,
                created_by=app_user,
            )

            company_id = auth_utils.generate_company_identiefier()
            while auth_models.Company.objects.filter(identifier=company_id).exists():
                company_id = auth_utils.generate_company_identiefier()

            company = auth_models.Company.objects.create(
                name=ticket.company_name,
                manager=app_user,
                address=address,
                domain=ticket.company_domain,
                identifier=company_id,
                EIN=ticket.EIN,
                scac=ticket.scac,
                fax_number=ticket.company_fax_number,
                phone_number=ticket.company_phone_number,
                company_size=ticket.company_size,
            )

            manager_models.Insurance.objects.create(
                company=company,
                provider=ticket.insurance_provider,
                policy_number=ticket.insurance_policy_number,
                type=ticket.insurance_type,
                premium_amount=ticket.insurance_premium_amount,
            )

            ticket.status = "Approved"
            ticket.save()

            utils.send_request_result(
                template="accepted_request.html",
                to=ticket.email,
                password_or_reason="",
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
                data={"details": "Ticket has been denied",
                      "ticket": serializers.ListTicketsSerializer(ticket).data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"details": "Action is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _create_app_user_from_ticket(self, ticket):
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

        EmailAddress.objects.create(
            user=user,
            email=ticket.email,
            verified=True,
            primary=True,
        )

        app_user = auth_models.AppUser.objects.create(
            user=user,
            phone_number=ticket.personal_phone_number,
            user_type="manager",
            selected_role="manager",
        )

        return app_user, password


class ListClaimView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsSupport]
    serializer_class = serializers.ListClaimSerializer
    queryset = Claim.objects.all().order_by("-created_at")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
