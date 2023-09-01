from django.http import QueryDict
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin 
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiTypes, inline_serializer
import authentication.permissions as permissions
import authentication.models as auth_models
import shipment.models as ship_models
import authentication.serializers as auth_serializers
import authentication.utilities as auth_utils
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework.generics import ListCreateAPIView , RetrieveAPIView

class CompanyView(GenericAPIView, CreateModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = auth_serializers.CompanySerializer
    queryset = auth_models.Company.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
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
        
class ListCreateTicketsView(ListCreateAPIView):
    """
    View for Listing and Creating the Tickets
    """
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    

class RetrieveTicketsView(RetrieveAPIView):
    """
    View for Retrieving the Tickets
    """
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    lookup_field = "id"     